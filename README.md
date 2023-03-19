# Markdown ChatGPT Connector

The Markdown ChatGPT Connector is a simple script for connecting Markdown and ChatGPT.

The script is designed so that developers can easily grasp the big picture and customize it to their own needs. Also, the purpose of the project is to show a simple implementation, not to satisfy a wide variety of needs. I encourage everyone to understand the source code and customize it to their own needs.

Forked from [scrapbox_chatgpt_connector](https://github.com/nishio/scrapbox_chatgpt_connector).

Ref: https://scrapbox.io/villagepump/Scrapbox_ChatGPT_Connector

## How to install

Install by pip:

```
$ pip install markdown_chatgpt_connector
```

Or you can use repository directly.
Install [Poetry](https://python-poetry.org/)
and run

```
$ poetry install
$ poetry run mcc ...
```

You can run `mcc` directly if you enter the poetry virtual environment:

```
$ poetry shell
```

## How to use

```
usage: mcc [-h] [-i INPUT] [-o OUTPUT] [-k KEY] [-q QUESTION] command

positional arguments:
  command               Command (index or ask)

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input markdown directory
  -o OUTPUT, --output OUTPUT
                        Output file (pickle
  -k KEY, --key KEY     OpenAI API key
  -q QUESTION, --question QUESTION
                        Question words for ask
```
