FROM python:3.12-alpine
WORKDIR /code
RUN apk add -u make poetry
COPY . .
RUN make install
ENTRYPOINT ["poetry", "run", "app"]
