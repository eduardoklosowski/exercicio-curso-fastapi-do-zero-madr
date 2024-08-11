#!/bin/bash

set -xe

# Completion
pipx install argcomplete
mkdir -p ~/.local/share/bash-completion/completions
echo 'eval "$(docker completion bash)"' > ~/.local/share/bash-completion/completions/docker
echo 'eval "$(register-python-argcomplete pipx)"' > ~/.local/share/bash-completion/completions/pipx

# Inicia projeto
make init
