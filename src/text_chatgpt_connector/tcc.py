import logging
import os
import pickle
import re
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import openai
import tiktoken
from tqdm import tqdm


@dataclass
class TCC:
    """OpenAI Chat Completion.

    Parameters
    ----------
    input_dir : str
        Path to the input directory including text files.
    input_suffix: str
        Comma separated suffixes of input files, by default "txt,md,markdown"
    output_file : str
        Path to the output pickle file.
    key : str
        OpenAI API key. If not given, try to get from environment variable: OPENAI_API_KEY.
    character_encoding: str
        Character encoding for input file, by default "utf-8"
    chat_model: str
        Chat model name, by default "gpt-3.5-turbo"
    encoding : str
        Encoding name for tiktoken , by default "cl100k_base"
    embedding : str
        Embedding model name, by default "text-embedding-ada-002"
    remain_url: bool
        Set to True to keep URL in the text, by default False (replace URL as "URL"
    keep_spaces: bool
        Set to True to keep spaces in the text, by default False (replace to single space)
    block_size : int
        Block size for embedding, by default 500
    embed_max_size : int
        Max size for embedding, by default 8150
    max_prompt_size : int
        Max size for prompt, by default 4096
    return_size : int
        Return size, by default 250
    prompt : str
        Prompt template.
    bare_prompt: str
        Prompt template without index.
    question : str
        Question template.
    no_index: bool
        Set to True to ask the question directly
    verbose: bool
        Set to True to show detailed log
    """

    input_dir: str = ""
    input_suffix: str = "txt,md,markdown"
    output_file: str = "index.pickle"
    key: str = ""
    character_encoding: str = "utf-8"
    chat_model: str = "gpt-3.5-turbo"
    encoding: str = "cl100k_base"
    embedding: str = "text-embedding-ada-002"
    remain_url: bool = False
    keep_spaces: bool = False
    block_size: int = 500
    embed_max_size: int = 8150  # actual limit is 8191
    max_prompt_size: int = 4097
    return_size: int = 250
    prompt: str = """Read the following text and answer the question. Your reply should be shorter than RETURN_SIZE characters.

## Text
{text}

## Question
{question}"""
    bare_prompt: str = """Answer the question. Your reply should be shorter than RETURN_SIZE characters.

## Question
{question}"""
    question: str = "What is the most important question?"
    no_index: bool = False
    verbose: bool = False

    def __post_init__(self) -> None:
        self.log = logging.getLogger(__name__)
        if self.verbose:
            if self.log.parent and self.log.parent.name != "root":
                self.log.parent.setLevel(logging.DEBUG)
            else:
                self.log.setLevel(logging.DEBUG)

        self.enc = tiktoken.get_encoding(self.encoding)
        self.prompt = self.prompt.replace(
            "RETURN_SIZE", str(self.return_size)
        ).strip()
        self.bare_prompt = self.bare_prompt.replace(
            "RETURN_SIZE", str(self.return_size)
        ).strip()
        self.question = self.question.strip()
        if not self.output_file.endswith(".pickle"):
            self.output_file = self.output_file + ".pickle"
        try:
            self.cache = pickle.load(open(self.output_file, "rb"))
        except FileNotFoundError:
            self.cache = {}

        self.gpt_3 = [
            "text-curie-001",
            "text-babbage-001",
            "text-gpt-ada-001",
            "davinci",
            "curie",
            "babbage",
            "ada",
        ]
        if self.chat_model in self.gpt_3:
            self.max_prompt_size = min(
                2049 - self.return_size, self.max_prompt_size
            )
        else:
            self.max_prompt_size = min(4097, self.max_prompt_size)

    def set_key(self, key: str = "") -> bool:
        if key:
            self.key = key
        if not self.key:
            self.key = os.environ.get("OPENAI_API_KEY", "")
        if not self.key:
            self.log.error(
                "Set OPEN_AI_API_KEY environment variable or use -k option"
            )
            return False
        openai.api_key = self.key
        return True

    def get_size(self, text: str) -> int:
        return len(self.enc.encode(text))

    def embed(self, text: str) -> list[float]:
        text = text.replace("\n", " ")
        tokens = self.enc.encode(text)
        if len(tokens) > self.embed_max_size:
            text = self.enc.decode(tokens[: self.embed_max_size])

        while True:
            try:
                res = openai.Embedding.create(
                    input=[text], model=self.embedding
                )
                time.sleep(1)
            except Exception as e:
                self.log.debug(e)
                time.sleep(1)
                continue
            break

        return res["data"][0]["embedding"]

    def get_files(self) -> list[Path]:
        path = Path(self.input_dir)
        files = []
        for suffix in self.input_suffix.split(","):
            files += list(path.glob(f"**/*.{suffix}"))
        if not files:
            self.log.error(
                f"No {', '.join(['*.' + x for x in self.input_suffix.split(',')])} found in {self.input_dir}."
            )
        return sorted(files, key=lambda x: x.name)

    def get_or_make(self, body: str, title: str) -> tuple[list[float], str]:
        if body not in self.cache:
            self.cache[body] = (self.embed(body), title)
            pickle.dump(self.cache, open(self.output_file, "wb"))
        return self.cache[body]

    def update_from_text(self) -> int:
        if not self.set_key():
            return 1
        if not self.input_dir:
            self.log.error("Set input directory")
            return 1
        files = self.get_files()
        if not files:
            self.log.error(
                f"No {', '.join(['*.' + x for x in self.input_suffix.split(',')])} found in {self.input_dir}."
            )
            return 1
        for f in tqdm(sorted(files)):
            buf = []
            title = f.name
            with open(f) as fp:
                for line in fp.readlines():
                    line = line.strip()
                    if not self.remain_url:
                        line = re.sub(r"https?://[^\s]+", "URL", line)
                    if not self.keep_spaces:
                        line = re.sub(r"[\s]+", " ", line)
                    buf.append(line)
                    body = " ".join(buf)
                    if self.get_size(body) > self.block_size:
                        self.get_or_make(body, title)
                        buf = buf[len(buf) // 2 :]
            body = " ".join(buf).strip()
            if body:
                self.get_or_make(body, title)
        return 0

    def get_sorted(self, query: str) -> list[tuple[float, str, str]]:
        q = np.array(self.embed(query))
        buf = []
        for body, (v, title) in tqdm(
            self.cache.items(), disable=not self.verbose
        ):
            buf.append((q.dot(v), body, title))
        buf.sort(reverse=True)
        return buf

    def ask(self) -> int:
        if not self.set_key():
            return 1
        prompt = self.bare_prompt if self.no_index else self.prompt
        prompt_size = self.get_size(prompt)
        rest = self.max_prompt_size - self.return_size - prompt_size
        if not self.question:
            self.log.error("Ask question!")
            return 1
        input_size = self.get_size(self.question)
        if rest < input_size:
            self.log.error("too large input!")
            return 1
        rest -= input_size

        if not self.no_index:
            samples = self.get_sorted(self.question)

            to_use = []
            used_title = []
            for _sim, body, title in samples:
                if title in used_title:
                    continue
                size = self.get_size(body)
                if rest < size:
                    break
                to_use.append(body)
                used_title.append(title)
                rest -= size
            text = "\n\n".join(to_use)
            prompt = prompt.format(question=self.question, text=text)
        else:
            prompt = prompt.format(question=self.question)

        self.log.debug("\nPROMPT:")
        self.log.debug(prompt)

        self.log.debug("\nTHINKING...")
        if self.chat_model in self.gpt_3:
            response = openai.Completion.create(
                model=self.chat_model,
                prompt=prompt,
                max_tokens=self.return_size,
                temperature=0.0,
            )
            content = response["choices"][0]["text"]
        else:
            response = openai.ChatCompletion.create(
                model=self.chat_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.return_size,
                temperature=0.0,
            )
            content = response["choices"][0]["message"]["content"]

        self.log.debug("\nRESPONSE:")
        self.log.debug(response)

        self.log.debug("\nANSWER:")
        self.log.info(f">>>> {self.question}")
        self.log.info(f"> {content}")
        if not self.no_index:
            self.log.info(f"\nref. {', '.join(used_title)}")
        return 0
