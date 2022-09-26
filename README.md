# helm-yaml-tui

A TUI navigator for rendered Helm YAML output with tree navigation and syntax highlighting.

Built with [Textual](https://github.com/Textualize/textual).

## Getting Started

### Installation

The easiest way to use `helm-yaml-tui` is through [pipx](https://pypa.github.io/pipx/),
which will create a clean environment for our installation and its dependencies:

```
$ pipx install helm-yaml-tui
```

Afterwards, you can execute `helm-yaml-tui` directly in your terminal.

Instead of installing with `pipx install`, you can also use `pipx run helm-yaml-tui`
whenever you want to execute `helm-yaml-tui` (see example below).

### Running `helm-yaml-tui`

`helm-yaml-tui` can directly consume the output from `helm template`:

```
$ helm repo add grafana https://grafana.github.io/helm-charts
$ helm repo update
$ helm template loki --namespace=loki grafana/loki-simple-scalable | pipx run helm-yaml-tui
```

<script id="asciicast-bHAfsPFXsCakImZdmxQLlE06q" src="https://asciinema.org/a/bHAfsPFXsCakImZdmxQLlE06q.js" async></script>
<noscript>
[![asciicast](https://asciinema.org/a/bHAfsPFXsCakImZdmxQLlE06q.svg)](https://asciinema.org/a/bHAfsPFXsCakImZdmxQLlE06q)
</noscript>
