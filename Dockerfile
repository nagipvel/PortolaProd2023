# pull official base image
# FROM python:3.8.0-alpine

# consider slim due to: https://github.com/docker-library/python/issues/381
FROM python:3.8-slim

# set work directory
WORKDIR /usr/src/Portola

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies for Alpine:
# RUN apk update \
#     && apk add postgresql-dev gcc python3-dev musl-dev

# install psycopg2 dependencies for Slim:
RUN apt-get update \
    && apt-get install -y gcc libpq-dev python-dev netcat dos2unix

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements/development.txt /usr/src/Portola/requirements.txt
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./scripts/entrypoint.sh /usr/src/Portola/entrypoint.sh

# Clean /r/n
# RUN dos2unix /entrypoint.sh && apt-get --purge remove -y dos2unix && rm -rf /var/lib/apt/lists/*

# Leaving stuff behind for dev:
RUN dos2unix /usr/src/Portola/entrypoint.sh

# copy project
COPY . /usr/src/Portola/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/Portola/entrypoint.sh"]
