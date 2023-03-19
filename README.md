# Text ChatGPT Connector

The Text ChatGPT Connector is a simple script for connecting text files and ChatGPT.

Forked from [scrapbox_chatgpt_connector](https://github.com/nishio/scrapbox_chatgpt_connector).

Ref: https://scrapbox.io/villagepump/Scrapbox_ChatGPT_Connector

## How to install

Install by pip:

```
$ pip install text_chatgpt_connector
```

Or you can use repository directly.
Install [Poetry](https://python-poetry.org/)
and run

```
$ poetry install
$ poetry run tcc ...
```

You can run \`tcc directly if you enter the poetry virtual environment:

```
$ poetry shell
```

## How to use

### Make index

To make index, run:

```
$ tcc index -i <input_dir>
```

`input_dir` is the directory which has text files (with suffix of `.txt`, `.md` or `.markdown` by default).

This will create pickle file named **index.pickle**.
If you want to change the name, set `-o <output_file>`.

If you run with different `input_dir` for the same `output_file`,
the index is appended to the previous one.

### Ask question

To ask a question, run:

```
$ tcc ask -q  "もっとも大事な問いとは何だろう？"
```

If you want compare the answer without index, run with `-n` (`--no_index`) option:

```
$ tcc ask -n -q  "もっとも大事な問いとは何だろう？"
```

### Usage

```
usage: tcc [-h] [-i INPUT_DIR] [-s INPUT_SUFFIX] [-o OUTPUT_FILE] [-k KEY] [-c CHARACTER_ENCODING] [--chat_model CHAT_MODEL]
           [--encoding ENCODING] [--embedding EMBEDDING] [--remain_url] [--keep_spaces] [--block_size BLOCK_SIZE]
           [--embed_max_size EMBED_MAX_SIZE] [--max_prompt_size MAX_PROMPT_SIZE] [--return_size RETURN_SIZE] [--prompt PROMPT]
           [--bare_prompt BARE_PROMPT] [-q QUESTION] [-n] [-v]
           [command]

positional arguments:
  command               Command (index or ask)

options:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input_dir INPUT_DIR
                        Input directory
  -s INPUT_SUFFIX, --input_suffix INPUT_SUFFIX
                        Comma separated suffixes of input files, "txt,md,markdown"
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Output file (pickle), default: "index.pickle"
  -k KEY, --key KEY     OpenAI API key. If not given, try to get from environment variable: OPENAI_API_KEY.
  -c CHARACTER_ENCODING, --character_encoding CHARACTER_ENCODING
                        Character encoding for input file, default: "utf-8"
  --chat_model CHAT_MODEL
                        Chat model name, default: "gpt-3.5-turbo"
  --encoding ENCODING   Encoding name for tiktoken, default: "cl100k_base"
  --embedding EMBEDDING
                        Embedding model name, default: "text-embedding-ada-002"
  --remain_url          Keep URL in the text
  --keep_spaces         Keep spaces in the text
  --block_size BLOCK_SIZE
                        Block size for embedding, default: 500
  --embed_max_size EMBED_MAX_SIZE
                        Max size for embedding, default: 8150
  --max_prompt_size MAX_PROMPT_SIZE
                        Max size for prompt, default: 4096
  --return_size RETURN_SIZE
                        Return size, default: 250
  --prompt PROMPT       Prompt template, default: "Read the following text and answer the question. Your reply should be shorter
                        than 250 characters. ## Text {text} ## Question {question}"
  --bare_prompt BARE_PROMPT
                        Prompt template without index, default: "Read the following text and answer the question. Your reply
                        should be shorter than 250 characters. ## Text {text} ## Question {question}"
  -q QUESTION, --question QUESTION
                        Question words for ask, default: "What is the most important question?"
  -n, --no_index        Ask the question directly
  -v, --version         Show version
```
