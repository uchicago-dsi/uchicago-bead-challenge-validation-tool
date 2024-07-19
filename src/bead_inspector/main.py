import argparse
from pathlib import Path

from bead_inspector.validator import BEADChallengeDataValidator


def check_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid integer value: '{value}'")


def main():
    parser = argparse.ArgumentParser(description="Validate NTIA Data.")
    parser.add_argument(
        "directory", type=str, help="The directory to check for the files."
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default="*",
        help="List of files (without .csv) to check for.",
    )
    parser.add_argument(
        "--results_dir",
        default=None,
        help="A dir to logs issues to (rather than printing to console).",
    )
    parser.add_argument(
        "-s",
        "--single_error_log_limit",
        default=20,
        type=check_int,
        help="Max number of issue-causing records to log.",
    )

    args = parser.parse_args()

    data_directory = Path(args.directory).resolve()
    BEADChallengeDataValidator(
        data_directory=data_directory,
        expected_data_formats=args.files,
        results_dir=args.results_dir,
        single_error_log_limit=args.single_error_log_limit,
    )


if __name__ == "__main__":
    main()
