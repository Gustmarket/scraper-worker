FROM python:3.9-bullseye

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt
RUN playwright install
RUN playwright install-deps

COPY . .

ENTRYPOINT []
