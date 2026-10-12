FROM python:3.14.8-alpine3.24

WORKDIR /usr/src/app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /usr/src/app/docker-entrypoint.sh

EXPOSE 8000

RUN adduser -D app
RUN chown -R app:app .
USER app

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]