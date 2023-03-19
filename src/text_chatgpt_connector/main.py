import argparse
import logging
import sys
from .__version__ import __version__

from .tcc import TCC


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    log = logging.getLogger(__name__.split(".")[0])
    log.setLevel(logging.INFO)

    tcc = TCC()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "command",
        help="Command (index or ask)",
        type=str,
        nargs="?",
    )
    arg_parser.add_argument(
        "-i",
        "--input_dir",
        help="Input directory",
        type=str,
    )
    arg_parser.add_argument(
        "-s",
        "--input_suffix",
        help=f"Comma separated suffixes of input files, \"{tcc.input_suffix}\"",
        type=str,
    )
    arg_parser.add_argument(
        "-o",
        "--output_file",
        help=f"Output file (pickle), default: \"{tcc.output_file}\"",
        type=str,
    )
    arg_parser.add_argument(
        "-k",
        "--key",
        help="OpenAI API key. If not given, try to get from environment variable: OPENAI_API_KEY.",
        type=str,
    )
    arg_parser.add_argument(
        "-c",
        "--character_encoding",
        help=f"Character encoding for input file, default: \"{tcc.character_encoding}\"",
        type=str,
    )
    arg_parser.add_argument(
        "--chat_model",
        help=f"Chat model name, default: \"{tcc.chat_model}\"",
        type=str,
    )
    arg_parser.add_argument(
        "--encoding",
        help=f"Encoding name for tiktoken, default: \"{tcc.encoding}\"",
        type=str,
    )
    arg_parser.add_argument(
        "--embedding",
        help=f"Embedding model name, default: \"{tcc.embedding}\"",
        type=str,
    )
    arg_parser.add_argument(
        "--block_size",
        help=f"Block size for embedding, default: {tcc.block_size}",
        type=str,
    )
    arg_parser.add_argument(
        "--embed_max_size",
        help=f"Max size for embedding, default: {tcc.embed_max_size}",
        type=int,
    )
    arg_parser.add_argument(
        "--max_prompt_size",
        help=f"Max size for prompt, default: {tcc.max_prompt_size}",
        type=int,
    )
    arg_parser.add_argument(
        "--return_size",
        help=f"Return size, default: {tcc.return_size}",
        type=int,
    )
    arg_parser.add_argument(
        "--prompt",
        help=f"Prompt template, default: \"{tcc.prompt}\"",
        type=str,
    )
    arg_parser.add_argument(
        "-q",
        "--question",
        help=f"Question words for ask, default: \"{tcc.question}\"",
        type=str,
    )
    arg_parser.add_argument(
        "-v",
        "--version",
        action='store_true',
        help="Show version",
    )

    args = arg_parser.parse_args()
    params = {}
    command = None
    for x in args.__dict__:
        if x == "version":
            if args.__dict__[x]:
                log.info(f"tcc {__version__}")
                return 0
        elif x == "command":
            command = args.__dict__[x]
        elif args.__dict__[x] is not None:
            params[x] = args.__dict__[x]

    if not command:
        log.error("No command specified")
        return 1

    tcc = TCC(**params)

    if args.command not in ["index", "ask"]:
        log.error(f"Invalid command: {args.command}. Must be index or ask")
        return 1
    elif args.command == "index":
        return tcc.update_from_text()
    elif args.command == "ask":
        return tcc.ask()

    return 0


if __name__ == "__main__":
    sys.exit(main())
