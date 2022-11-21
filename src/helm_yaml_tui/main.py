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
from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree, Static, Footer, Header
from textual.reactive import var
from textual.containers import Horizontal, Vertical

from helm_yaml_tui.loader import HelmTemplateLoader


class HelmYamlTui(App):
    CSS_PATH = "helm_yaml_tui.css"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("b", "toggle_browser", "Toggle File Browser"),
    ]

    show_tree = var(True)

    def __init__(self, directory: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory = directory

    def on_shutdown_request(self, event: events.ShutdownRequest) -> None:
        self.directory.unlink()
        super().on_shutdown_request(event)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Vertical(DirectoryTree(str(self.directory)), id="tree-view"),
            Vertical(Static(id="file", expand=True), id="file-view"),
        )
        yield Footer()

    def on_mount(self, event: events.Mount) -> None:
        self.query_one(DirectoryTree).focus()

    def on_directory_tree_file_click(self, message: DirectoryTree.FileClick) -> None:
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

        self.app.sub_title = str(Path(message.path).relative_to(self.directory))

        code = self.query_one("#file", Static)
        code.update(syntax)

    def action_toggle_browser(self):
        self.show_tree = not self.show_tree

    def watch_show_tree(self, show_tree: bool) -> None:
        self.set_class(show_tree, "-show-tree")


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

    HelmYamlTui(directory=yaml_dir).run()


if __name__ == "__main__":
    main()
