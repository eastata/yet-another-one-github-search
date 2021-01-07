FROM python:3.9.0-alpine

LABEL org.opencontainers.image.source https://github.com/eastata/yet-another-one-github-search

RUN apk add --no-cache --virtual .build-deps gcc musl-dev

WORKDIR /env
ADD ./requirements.txt .
RUN pip install -r ./requirements.txt
COPY ./queries ./queries
COPY ./main.py .

ENTRYPOINT ["/env/main.py"]
CMD []
