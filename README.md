# RAG tutorial

Docker Compose runs three services: the API, a Postgres database with pgvector, and a Scrapy scraper.

## Start

Clone the repo and move into it:

```bash
git clone https://github.com/mmmohajer/rag_tutorial.git
cd rag_tutorial
```

Copy the sample env files and fill them in:

```bash
cp secrets/db/.env.sample secrets/db/.env
cp secrets/api/.env.sample secrets/api/.env
cp secrets/scraper/.env.sample secrets/scraper/.env
```

`secrets/db/.env` can stay as the sample (`rag` / `rag` / `rag`). Point the API at that database and add an OpenAI key:

```
APP_NAME=rag-api
DB_HOST=db
DB_PORT=5432
DB_USER=rag
DB_PASSWORD=rag
DB_NAME=rag
OPEN_AI_API_KEY=
```

The scraper calls the API over the Compose network. Set `SITE_URL` to the address of the website you want to scrape:

```
API_URL=http://api:8000
SITE_URL=
```

Page paths live in `scraper/target_site/spiders/constants.py` as `PAGE_PATHS`. Each path is joined onto `SITE_URL`, so update that list to the real pages of the site you put in `SITE_URL` before you crawl. An empty string is the homepage.

Not every site allows this crawler. It only requests the paths in `PAGE_PATHS`, and it obeys `robots.txt`. If that file disallows a path, or disallows the user agent `SiteBot/1.0`, Scrapy skips the page and it is not saved. A site can also block the request when `robots.txt` allows it, for example with a login wall or a firewall. Those pages fail instead of being stored.

Build and start:

```bash
docker compose up -d --build
```

The API waits for Postgres, runs migrations, then listens on [http://localhost:8000](http://localhost:8000). Requests are in `api.http`.

Python code is mounted into the containers. Restart a service after you change it so the process reloads:

```bash
docker compose restart api
```

## Scrape

The scraper container stays running. From the project directory:

```bash
docker compose exec scraper scrapy crawl pages
```

Inside the container the same command is:

```bash
scrapy crawl pages
```
