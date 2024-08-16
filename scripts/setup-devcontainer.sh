#!/bin/bash

set -xe

# Config docker
sudo sh -c 'echo "{\"insecure-registries\": [\"192.168.0.0/16\"]}" > /etc/docker/daemon.json'
sudo killall dockerd
/usr/local/share/docker-init.sh

# Config poetry
poetry config virtualenvs.in-project true
[ -e .venv ] || poetry env use /usr/local/bin/python

# Config minikube
minikube config set driver docker

# Setup yq
sudo wget -O/usr/local/bin/yq https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_amd64
sudo chmod +x /usr/local/bin/yq

# Completion
pipx install argcomplete
mkdir -p ~/.local/share/bash-completion/completions
echo 'eval "$(docker completion bash)"' > ~/.local/share/bash-completion/completions/docker
echo 'eval "$(register-python-argcomplete pipx)"' > ~/.local/share/bash-completion/completions/pipx
echo 'eval "$(poetry completions bash)"' > ~/.local/share/bash-completion/completions/poetry
echo 'eval "$(minikube completion bash)"' > ~/.local/share/bash-completion/completions/minikube
echo 'eval "$(helm completion bash)"' > ~/.local/share/bash-completion/completions/helm

# Inicia projeto
make init
