from argparse import ArgumentParser, Namespace
from pathlib import Path

from src.folder_files import FolderFiles
from src.gherkin_custom_types import load_gherkin_custom_types
from src.gherkin_glossary import GherkinTermGlossary


def parse_args() -> Namespace:
    parser = ArgumentParser(description="")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-d",
        "--starting-directory",
        type=Path,
        help="Parent directory to search recurisvely and build `FolderFiles` object",
    )
    group.add_argument(
        "-i",
        "--input-folder-files",
        type=Path,
        help="`FolderFiles` json output from previous script run to be used as input \
        for current script run",
    )

    parser.add_argument(
        "-e",
        "--extensions",
        nargs="+",
        required=False,
        default=".feature",
        help="File extensions to include. Provide as space separated list after flag.",
    )
    parser.add_argument(
        "-o",
        "--folder-files-output",
        type=Path,
        required=False,
        help="Directory to create json output from `FolderFiles` object. \
        Used only if -d flag specified.",
    )
    parser.add_argument(
        "-g",
        "--gherkin-glossary-output",
        type=Path,
        required=True,
        help="Directory to create json output from `GherkinTermGlossary` object.",
    )
    parser.add_argument(
        "-t",
        "--custom-gherkin-types",
        type=Path,
        required=False,
        help="Path to json with gherkin custom types to be used in \
        building `GherkinTermGlossary`",
    )
    parser.add_argument(
        "-s",
        "--schema",
        required=False,
        default=Path("./schema.json"),
        help="Path to schema.json for custom gherkin types .json input",
    )

    return parser.parse_args()


def run() -> None:
    args = parse_args()

    folder_files: FolderFiles
    extensions = tuple(args.extensions)

    if args.starting_directory:
        folder_files = FolderFiles.populate(args.starting_directory, extensions)

        if args.folder_files_output:
            folder_files.dump(args.folder_files_output)

    else:
        folder_files = FolderFiles.load(args.input_folder_files)

    content = folder_files.get_content()

    custom_types = None
    if args.custom_gherkin_types:
        custom_types = load_gherkin_custom_types(args.custom_gherkin_types, args.schema)

    glossary = GherkinTermGlossary(content, custom_types)
    glossary.dump(args.gherkin_glossary_output)
