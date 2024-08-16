# Projeto Final do FastAPI do Zero - Meu Acervo Digital de Romances

Esse é meu projeto final do curso [FastAPI do Zero](https://fastapidozero.dunossauro.com/). Mas informações podem ser vistas [aqui](https://fastapidozero.dunossauro.com/14/).

## Ferramentas

- [EditorConfig](https://editorconfig.org/): Auxiliar a configuração do editor (charset, formato de quebra de linha, indentação dos diferentes tipos de arquivos, espaços no final das linhas, quebra de linha no final dos arquivos).
- [Dev Containers](https://containers.dev/): Criar ambiente de desenvolvimento dentro de um contêiner Docker de forma automatizada, não exigindo nenhuma configuração manual.
- [GNU Make](https://www.gnu.org/software/make/): Executar comandos no projeto.
- [GitHub Actions](https://docs.github.com/pt/actions): Executar os lints e testes no servidor.
- [Poetry](https://python-poetry.org/): Gerenciar o projeto Python e controlar as dependências.
- [Ruff](https://docs.astral.sh/ruff/): Formatador e regras de lint para o código Python.
- [mypy](https://www.mypy-lang.org/): Varifica erros de tipos no código Python.
- [pytest](https://docs.pytest.org/en/stable/): Testes automatizados no código Python.
- [minikube](https://minikube.sigs.k8s.io/docs/): Gerencia cluster Kubernetes local para testes.
- [Helm](https://helm.sh/pt/): Gerencia recursos da aplicação criados no Kubernetes.

## Como configurar o projeto para desenvolvimento local?

A configuração do projeto ocorre de forma automática pelo [Development Containers](https://containers.dev/), bastando ter o [Docker](https://docs.docker.com/engine/install/) instalado e abrir o projeto no editor. No [Visual Studio Code](https://code.visualstudio.com/) é necessário ter a extensão [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) instalada, após isso basta abrir o projeto que o próprio Visual Studio Code sugerirá reabri-lo dentro do contêiner.

Caso não queira utilizar um editor específico, é possível construir o ambiente utilizando o pacote [CLI](https://www.npmjs.com/package/@devcontainers/cli).

## Executa lints e testes no commit

É possível executar os lints e testes a cada commit, garantindo que os mesmos estejam passando antes do commit seja realizado. Para isso basta executar o seguinte comando a baixo:

```sh
cat > .git/hooks/pre-commit << EOF
#!/bin/sh
make lint test
EOF
chmod +x .git/hooks/pre-commit
```

## Kubernetes

Esse projeto pode ser executado no [Kubernetes](https://kubernetes.io/pt-br/), para isso o [minikube] está disponível no dev container para testá-lo localmente.

Para iniciar um cluster do Kubernetes local, execute o seguinte comando:

```sh
make minikube-start
```

Para parar a execução do cluster Kubernetes, basta executar o comando:

```sh
make minikube-stop
```

Dessa forma é possível usar o comando de iniciar para executá-lo novamente. Para apagar o cluster, é possível usar o comando:

```sh
make minikube-delete
```

Opcionalmente é possível acessar um dashboard do Kubernetes quando ele está executando com o comando:

```sh
make minikube-dashboard
```

O deploy da aplicação pode ser feita utilizando o comando:

```sh
make minikube-run-app
```

Após isso é possível acessar a API atráves do endereço mostrado na tela ou por http://localhost:8000/.

A aplicação também pode ser removida do Kubernetes com o comando:

```sh
make minikube-delete-app
```
