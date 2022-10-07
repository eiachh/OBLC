#!/bin/bash

eval $(minikube docker-env)
docker build -t eiachh/oblc ./
docker rmi $(docker images --filter "dangling=true" -q --no-trunc)