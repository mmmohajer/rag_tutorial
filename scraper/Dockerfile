FROM python:3.14.8-alpine3.24

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["scrapy", "crawl", "pages"]
