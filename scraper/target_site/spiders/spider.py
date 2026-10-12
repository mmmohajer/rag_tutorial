import json
import urllib.error
import urllib.request

import scrapy

from settings import settings
from target_site.spiders.constants import PAGE_PATHS
from target_site.utils import chunk_content


class PagesSpider(scrapy.Spider):
    name = "pages"
    start_urls = [settings.site_url.rstrip("/") + path for path in PAGE_PATHS]

    def _list_pages(self) -> list[dict]:
        request = urllib.request.Request(settings.api_url.rstrip("/") + "/rag/pages")
        with urllib.request.urlopen(request, timeout=60) as api_response:
            return json.load(api_response)

    def _save_page(self, title: str, url: str) -> int:
        payload = json.dumps({"title": title, "url": url}).encode()
        request = urllib.request.Request(
            settings.api_url.rstrip("/") + "/rag/pages",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as api_response:
                page = json.load(api_response)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API returned {exc.code} while creating {url}: {body}") from exc
        return page["id"]

    def _delete_page(self, page_id: int) -> None:
        request = urllib.request.Request(
            settings.api_url.rstrip("/") + f"/rag/pages/{page_id}",
            method="DELETE",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as api_response:
                api_response.read()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API returned {exc.code} while deleting page {page_id}: {body}") from exc

    def _save_chunk(self, page_id: int, chunk_number: int, chunk_text: str) -> None:
        payload = json.dumps(
            {
                "page_id": page_id,
                "chunk_number": chunk_number,
                "chunk_text": chunk_text,
            }
        ).encode()
        request = urllib.request.Request(
            settings.api_url.rstrip("/") + "/rag/chunks",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as api_response:
                api_response.read()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"API returned {exc.code} for page {page_id} chunk {chunk_number}: {body}"
            ) from exc

    async def start(self):
        self.page_ids_by_url = {page["url"]: page["id"] for page in self._list_pages()}
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        texts = response.xpath(
            "//body//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::noscript)]"
        ).getall()
        content = " ".join(part.strip() for part in texts if part.strip())
        title = " ".join((response.css("title::text").get() or response.url).split())
        page_id = self.page_ids_by_url.get(response.url)
        if page_id is not None:
            self._delete_page(page_id)
        pieces = list(enumerate(chunk_content(content), start=1))
        if pieces:
            page_id = self._save_page(title, response.url)
            for number, piece in pieces:
                self._save_chunk(page_id, number, piece)
                yield {
                    "url": response.url,
                    "title": title,
                    "chunk_number": number,
                    "content": piece,
                }
        self.logger.info("Page completed successfully: %s — %s", response.url, title)
