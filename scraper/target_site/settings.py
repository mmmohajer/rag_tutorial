import os

BOT_NAME = "target_site"
SPIDER_MODULES = ["target_site.spiders"]
NEWSPIDER_MODULE = "target_site.spiders"

LOG_LEVEL = "INFO"
ROBOTSTXT_OBEY = True
_site_url = os.environ.get("SITE_URL", "").rstrip("/")
USER_AGENT = f"SiteBot/1.0 (+{_site_url})" if _site_url else "SiteBot/1.0"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
