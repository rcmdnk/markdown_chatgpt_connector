import argparse
import logging
import sys

from .mcc import MCC


def main() -> int:
    log = logging.getLogger(__name__.split(".")[0])
    log.setLevel(logging.INFO)

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "command",
        help="Command (index or ask)",
        type=str,
    )
    arg_parser.add_argument(
        "-i",
        "--input_dir",
        help="Input markdown directory",
        type=str,
    )
    arg_parser.add_argument(
        "-o",
        "--output_file",
        help="Output file (pickle)",
        type=str,
    )
    arg_parser.add_argument(
        "-k",
        "--key",
        help="OpenAI API key",
        type=str,
    )
    arg_parser.add_argument(
        "-c",
        "--character_encoding",
        help="",
        type=str,
    )
    arg_parser.add_argument(
        "--block_size",
        help="Block size for embedding",
        type=str,
    )
    arg_parser.add_argument(
        "--embed_max_size",
        help="Max size for embedding",
        type=int,
    )
    arg_parser.add_argument(
        "--encoding",
        help="Encoding name for tiktoken",
        type=str,
    )
    arg_parser.add_argument(
        "--embedding",
        help="Embedding model name",
        type=str,
    )
    arg_parser.add_argument(
        "--max_prompt_size",
        help="Max size for prompt",
        type=int,
    )
    arg_parser.add_argument(
        "--return_size",
        help="Return size",
        type=int,
    )
    arg_parser.add_argument(
        "--prompt",
        help="Prompt template",
        type=str,
    )
    arg_parser.add_argument(
        "-q",
        "--question",
        help="Question words for ask",
        type=str,
    )
    args = arg_parser.parse_args()
    params = {}
    command = None
    for x in args.__dict__:
        if x == "command":
            command = args.__dict__[x]
        elif args.__dict__[x] is not None:
            params[x] = args.__dict__[x]
    if not command:
        log.error("No command specified")
        return 1

    mcc = MCC(**params)
    return 0
    if args.command not in ["index", "ask"]:
        log.error(f"Invalid command: {args.command}. Must be index or ask")
        return 1
    if args.command == "index":
        return mcc.update_from_markdown()
    if args.command == "ask":
        mcc.ask()

    return 0


if __name__ == "__main__":
    sys.exit(main())
