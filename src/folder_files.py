from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from itertools import chain
from pathlib import Path
from typing import Any, Iterator


@dataclass
class FileContent:
    file: Path
    content: list[str]


@dataclass
class FolderFiles:
    directory: Path
    files: list[FileContent]
    children: list[FolderFiles]

    def __iter__(self) -> Iterator[Any]:
        """
        Iterate over properties and values as dictionary key value pairs
        """
        return iter(asdict(self).items())

    @classmethod
    def populate(
        cls, parent_directory_path: Path, include_file_types: tuple[str, ...]
    ) -> FolderFiles:
        """
        Create `FolderFiles` representation of a directory structure, the files in each
        of those directories, and of those files, their contents.

        `include_file_types` are the file extensions to be included; others are ignored.
        """
        files, children = [], []

        for directory in parent_directory_path.glob("*"):
            if directory.is_file() and directory.suffix.endswith(include_file_types):
                content = [line.strip() for line in directory.open().readlines()]
                files.append(FileContent(directory, content))
            elif directory.is_dir():
                children.append(cls.populate(directory, include_file_types))

        return FolderFiles(parent_directory_path, files, children)

    @classmethod
    def load(cls, json_file_path: Path) -> FolderFiles:
        """
        Get `FolderFiles` instance from `.json` file.
        """
        return cls._load_json_dict(json.load(open(json_file_path, "r")))

    @classmethod
    def _load_json_dict(
        cls,
        json_dict: dict[str, Any],
    ) -> FolderFiles:
        # Convert json dictionary to `FolderFiles` object, resolving path string to
        # Path objects
        files, children = [], []
        for key, value in json_dict.items():
            if key == "files":
                for file_path in value:
                    files.append(
                        FileContent(Path(file_path["file"]), file_path["content"])
                    )
            elif key == "children" and value:
                for item in value:
                    children.append(cls._load_json_dict(item))
        return FolderFiles(
            Path(json_dict["directory"]),
            files,
            children,
        )

    def _stringify(self) -> dict[str, str | list[str] | list[dict[str, Any]]]:
        # Convert Path objects into strings (of their resolved paths) so that a
        # `FolderFiles` object can be serialised.
        #
        # Private method as __dict__ or dataclasses.asdict() can be used to transform
        # `FolderFiles` to dictionary (while preserving Path object values)
        files, children = [], []
        for key, value in self:
            if key == "files":
                for file_path in value:
                    files.append(
                        {
                            "file": file_path["file"].resolve().__str__(),
                            "content": file_path["content"],
                        }
                    )
            elif key == "children" and value:
                for item in value:
                    children.append(FolderFiles(**item)._stringify())
        return {
            "directory": self.directory.resolve().__str__(),
            "files": files,
            "children": children,
        }

    def json(self, indent: int = 2) -> str:
        """
        Returns json string representation of FolderFiles
        """
        return json.dumps(self._stringify(), indent=indent)

    def dump(self, output_path: Path, indent: int = 2) -> None:
        """
        Creates json file from `FolderFiles`
        """
        json.dump(self._stringify(), open(output_path, "w"), indent=indent)

    def get_content(self) -> list[str]:
        """
        Get all nested file contents as a single list of strings.
        Each entry in the list is a line of text in a given file.
        """
        content = []
        for key, value in self:
            if key == "files" and value:
                content.extend([item["content"] for item in value])
            elif key == "children":
                content.extend([child.get_content() for child in self.children])
        return list(chain.from_iterable(content))
