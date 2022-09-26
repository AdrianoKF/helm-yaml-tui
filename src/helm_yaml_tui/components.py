import tempfile
from pathlib import Path

from textual.widgets import DirectoryTree


class VirtualDirectoryTree(DirectoryTree):
    def __init__(self, files: dict[str, str], name: str = None) -> None:
        tempdir = tempfile.mkdtemp(prefix="helm-yaml-tui-")
        for filename, content in files.items():
            path = Path(tempdir) / filename
            path.parent.mkdir(exist_ok=True, parents=True)
            path.write_text(content)
        super().__init__(tempdir, name)
