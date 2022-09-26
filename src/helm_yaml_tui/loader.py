import io
import re
import sys
from pathlib import Path
from typing import Optional

from ruamel.yaml import YAML

_SOURCE_PATTERN = re.compile(r"Source: (?P<file>.*)")


class HelmTemplateLoader:
    def __init__(self, path: Optional[Path] = None):
        input_stream = None
        if path:
            input_stream = path.read_text(encoding="utf-8")
        else:
            input_stream = sys.stdin

        self.docs = {}
        yaml = YAML(typ="rt")
        yaml.allow_duplicate_keys = True
        for doc in yaml.load_all(input_stream):
            source = str(doc.ca.comment[1][0].value).strip()
            source_file = _SOURCE_PATTERN.search(source).group("file")

            writer = io.StringIO()
            yaml.dump(doc, writer)
            self.docs[source_file] = writer.getvalue()
            writer.close()

    def to_directory(self, output_dir: Path):
        assert output_dir.is_dir()
        for filename, content in self.docs.items():
            path = Path(output_dir) / filename
            path.parent.mkdir(exist_ok=True, parents=True)
            path.write_text(content)
