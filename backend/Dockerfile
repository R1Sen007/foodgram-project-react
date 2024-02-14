FROM python:3.9

WORKDIR /app

COPY Makefile .

RUN make install

COPY requirements.txt .

RUN make requirements

COPY . .

CMD ["make", "run"]