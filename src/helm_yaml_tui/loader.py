"""Functionality for working with multi-document YAML files as produced by Helm."""

import io
import re
import sys
from pathlib import Path
from typing import Optional

from ruamel.yaml import YAML

_SOURCE_PATTERN = re.compile(r"Source: (?P<file>.*)")


class HelmTemplateLoader:
    """HelmTemplateLoader parses multi-document YAML files."""

    def __init__(self, path: Optional[Path] = None):
        """Construct a new HelmTemplateLoader instance for a given YAML document.

        Args:
            path (Optional[Path], optional): Input YAML document. If set to `None`, input is read from `sys.stdin`.
        """
        input_stream = None
        if path:
            input_stream = path.read_text(encoding="utf-8")
        else:
            input_stream = sys.stdin

        self.docs: dict[str, str] = {}
        yaml = YAML(typ="rt")
        yaml.allow_duplicate_keys = True
        for doc in yaml.load_all(input_stream):
            source = str(doc.ca.comment[1][0].value).strip()
            match = _SOURCE_PATTERN.search(source)
            if not match:
                print(f"No file name found for: {source}")
                continue

            source_file = match.group("file")

            writer = io.StringIO()
            yaml.dump(doc, writer)
            if (current := self.docs.get(source_file)) is None:
                self.docs[source_file] = writer.getvalue()
            else:
                self.docs[source_file] = current + "\n---\n" + writer.getvalue()
            writer.close()

    def to_directory(self, output_dir: Path):
        """Save the individual YAML documents from the input to an output directory.

        Args:
            output_dir (Path): Output directory for saving, will be created if it does not exist.
        """
        assert output_dir.is_dir()
        for filename, content in self.docs.items():
            path = Path(output_dir) / filename
            path.parent.mkdir(exist_ok=True, parents=True)
            path.write_text(content)
