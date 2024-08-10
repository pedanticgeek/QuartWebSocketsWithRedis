FROM python:3.11-slim-bookworm as base

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYHTONUNBUFFERED=1

RUN python -m pip install poetry

EXPOSE 80

WORKDIR /app

COPY ./backend /app/

RUN poetry install
