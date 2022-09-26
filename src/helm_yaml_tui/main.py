import argparse
import atexit
import os.path
import sys
import tempfile
from pathlib import Path

from rich.console import RenderableType
from rich.syntax import Syntax
from rich.traceback import Traceback
from textual import events
from textual.app import App
from textual.widgets import DirectoryTree, FileClick, ScrollView

from helm_yaml_tui.loader import HelmTemplateLoader


class HelmYamlTui(App):
    def __init__(self, directory: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory = directory

    async def on_load(self) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_shutdown_request(self, event: events.ShutdownRequest) -> None:
        self.directory.unlink()
        return await super().on_shutdown_request(event)

    async def on_mount(self) -> None:
        self.tree = DirectoryTree(str(self.directory), "Files")
        self.body = ScrollView()

        await self.view.dock(ScrollView(self.tree), edge="left", size=40)
        await self.view.dock(self.body, edge="right")

    async def handle_file_click(self, message: FileClick) -> None:
        """A message sent by the directory tree when a file is clicked."""

        syntax: RenderableType
        try:
            # Construct a Syntax object for the path in the message
            syntax = Syntax.from_path(
                message.path,
                line_numbers=True,
                word_wrap=True,
                indent_guides=True,
                theme="monokai",
            )
        except Exception:
            # Possibly a binary file
            # For demonstration purposes we will show the traceback
            syntax = Traceback(theme="monokai", width=None, show_locals=True)
        self.app.sub_title = os.path.basename(message.path)
        await self.body.update(syntax)


def main():
    parser = argparse.ArgumentParser(prog="helm-yaml-tui")
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        help="Path to Helm template output YAML",
        default=None,
    )

    cmdargs = parser.parse_args()

    loader = HelmTemplateLoader(path=cmdargs.path)

    # Restore stdin to a TTY for Textual
    if not cmdargs.path:
        sys.stdin = open("/dev/tty", "rb")
        atexit.register(lambda: sys.stdin.close())

    tempdir = Path(tempfile.mkdtemp("helm-yaml-tui-"))
    loader.to_directory(tempdir)

    yaml_dir = tempdir

    # Don't show temp dir as root if it contains a singular subfolder
    contents = list(tempdir.iterdir())
    if len(contents) == 1:
        yaml_dir = contents[0]

    HelmYamlTui.run(directory=yaml_dir)


if __name__ == "__main__":
    main()
