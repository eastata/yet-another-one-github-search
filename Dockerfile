FROM python:3.9.0-alpine

RUN apk add --no-cache --virtual .build-deps gcc musl-dev

WORKDIR /env
ADD ./requirements.txt .
RUN pip install -r ./requirements.txt
COPY ./queries ./queries
COPY ./main.py .

ENTRYPOINT ["/env/main.py"]
CMD []
