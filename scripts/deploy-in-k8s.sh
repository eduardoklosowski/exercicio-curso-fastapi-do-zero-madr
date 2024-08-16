#!/bin/bash

set -e

# Image
api_image="$(minikube ip):5000/madr/api:latest"
docker build -t "$api_image" .
docker push "$api_image"

# Config
[ -e "$1" ] || cp chart/values.yaml "$1"
yq -i ".host = \"madr.$(minikube ip).nip.io\"" "$1"
yq -i ".images.api = \"$api_image\"" "$1"

# Deploy
if [ "$(helm ls -qf '^madr$' | wc -l)" -eq "0" ]; then
    helm install --values="$1" madr chart
else
    helm upgrade --values="$1" madr chart
fi

# Info
echo "URL: http://$(yq -r '.host' k8s-values.yaml)/"
