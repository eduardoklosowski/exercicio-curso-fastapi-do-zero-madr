#!/bin/bash

set -xe

# Completion
mkdir -p ~/.local/share/bash-completion/completions
echo 'eval "$(docker completion bash)"' > ~/.local/share/bash-completion/completions/docker
