#!/bin/bash

# Pull the latest images
docker-compose pull

# Recreate and start the containers
docker-compose up -d
