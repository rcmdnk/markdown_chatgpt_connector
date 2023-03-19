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
class MCC:
    """OpenAI Chat Completion.

    Parameters
    ----------
    input_dir : str
        Path to the input file.
    output_file : str
        Path to the output file.
    key : str
        OpenAI API key. If not given, try to get from environment variable: OPENAI_API_KEY.
    block_size : int
        Block size for embedding, by default 500
    embed_max_size : int
        Max size for embedding, by default 8150
    encoding : str
        Encoding name, by default "cl100k_base"
    embedding : str
        Embedding model name, by default "text-embedding-ada-002"
    max_prompt_size : int
        Max size for prompt, by default 4096
    return_size : int
        Return size, by default 250
    prompt : str
        Prompt template.
    question : str
        Question template.
    """

    input_dir: str
    output_file: str
    key: str
    block_size: int = 500
    embed_max_size = 8150  # actual limit is 8191
    encoding: str = "cl100k_base"
    embedding: str = "text-embedding-ada-002"
    max_prompt_size: int = 4096
    return_size: int = 250
    prompt: str = """Read the following text and answer the question. Your reply should be shorter than 250 characters.

## Text
{text}

## Question
{input}"""
    question: str = ""

    def __post_init__(self) -> None:
        self.log = logging.getLogger(__name__)
        self.enc = tiktoken.get_encoding(self.encoding)
        self.prompt = self.prompt.strip()
        self.question = self.question.strip()
        try:
            self.cache = pickle.load(open(self.output_file, "rb"))
        except FileNotFoundError:
            self.cache = {}

    def set_key(self, key: str = "") -> bool:
        if key is not None:
            self.key: str = key
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
                self.log.info(e)
                time.sleep(1)
                continue
            break

        return res["data"][0]["embedding"]

    def get_or_make(self, body: str, title: str) -> tuple[list[float], str]:
        if body not in self.cache:
            self.cache[body] = (self.embed(body), title)
            pickle.dump(self.cache, open(self.output_file, "wb"))
        return self.cache[body]

    def update_from_markdown(self) -> int:
        if not self.set_key():
            return 1
        path = Path(self.input_dir)
        md_files = list(path.glob("**/*.md"))
        md_files += list(path.glob("**/*.markdown"))
        for f in tqdm(sorted(md_files)):
            buf = []
            title = f.name
            with open(f) as fp:
                for line in fp.readlines():
                    line = line.strip()
                    line = re.sub(r"https?://[^\s]+", "URL", line)
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
        for body, (v, title) in tqdm(self.cache.items()):
            buf.append((q.dot(v), body, title))
        buf.sort(reverse=True)
        return buf

    def ask(self) -> int:
        if not self.set_key():
            return 1
        prompt_size = self.get_size(self.prompt)
        rest = self.max_prompt_size - self.return_size - prompt_size
        if not self.question:
            self.log.error("Ask question!")
            return 1
        input_size = self.get_size(self.question)
        if rest < input_size:
            self.log.error("too large input!")
            return 1
        rest -= input_size
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
            self.log.info("\nUSE:", title, body)
            rest -= size

        text = "\n\n".join(to_use)
        prompt = self.prompt.format(input=self.question, text=text)

        self.log.info("\nPROMPT:")
        self.log.info(prompt)

        self.log.info("\nTHINKING...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.return_size,
            temperature=0.0,
        )

        self.log.info("\nRESPONSE:")
        self.log.info(response)
        content = response["choices"][0]["message"]["content"]

        self.log.info("\nANSWER:")
        self.log.info(f">>>> {self.question}")
        self.log.info(">", content)
        self.log.info("\nref.", *[f"[{s}]" for s in used_title])
        return 0
