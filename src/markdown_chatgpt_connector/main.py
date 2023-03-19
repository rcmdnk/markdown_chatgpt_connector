import argparse
import logging
import sys

from .mcc import MCC


def main() -> int:
    log = logging.getLogger(__name__.split(".")[0])
    log.setLevel(logging.INFO)

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "command", help="Command (index or ask)", default=""
    )
    arg_parser.add_argument(
        "-i", "--input", help="Input markdown directory", default="."
    )
    arg_parser.add_argument(
        "-o",
        "--output",
        help="Output file (pickle",
        default="markdown.pickle",
    )
    arg_parser.add_argument("-k", "--key", help="OpenAI API key", default="")
    arg_parser.add_argument(
        "-q",
        "--question",
        help="Question words for ask",
        default="もっとも大事な問いとは何だろう？",
    )
    args = arg_parser.parse_args()

    if args.command == "":
        log.error("No command specified")
        return 1

    mcc = MCC(
        input_dir=args.input,
        output_file=args.output,
        key=args.key,
        question=args.question,
    )
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
