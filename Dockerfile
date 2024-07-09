FROM python:3.11-slim-bookworm as base

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYHTONUNBUFFERED=1

RUN python -m pip install pipenv

EXPOSE 80

COPY ./Pipfile /app/
COPY ./Pipfile.lock /app/
WORKDIR /app
RUN pipenv install

COPY ./backend /app/
