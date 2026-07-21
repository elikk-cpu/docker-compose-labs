#!/usr/bin/env sh
docker run -d --name docker-lab-fixed-name alpine:3.22.2   sh -c 'while true; do sleep 60; done'
