#!/bin/bash
docker build . -t wcladremover && docker run -v "$(pwd)"/output:/output wcladremover:latest