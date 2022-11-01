#!/bin/bash

userInput="n"
git fetch
gitstatus=$(git status)
if [[ $gitstatus == *"Your branch is behind"* ]]; then
    echo "Your branch is behind, do you want to pull first? (y/n)"
    read userInput
fi

if [[ $userInput == "y" ]]; then
    git pull
fi

git submodule update --init --recursive

eval $(minikube docker-env)
docker build -t eiachh/oblc ./
docker rmi $(docker images --filter "dangling=true" -q --no-trunc)