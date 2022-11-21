from helm_yaml_tui import loader

from pathlib import Path


def test_loader_multiple_docs(tmp_path: Path) -> None:
    document = tmp_path / "document.yaml"
    document.write_text(
        """
# Source: a.yaml
foo: bar
---
# Source: a.yaml
bar: 42
---
# Source: a.yaml
baz: False
""".strip()
    )

    dut = loader.HelmTemplateLoader(document)
    assert len(dut.docs) == 1
    assert dut.docs["a.yaml"].count("\n---\n") == 2
