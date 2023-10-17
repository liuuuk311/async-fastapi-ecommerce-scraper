import locale
import re
import string
from datetime import datetime
from operator import itemgetter
from random import choice
from typing import List, Optional, Union, Tuple
from unicodedata import normalize
from urllib.parse import urljoin

import aiohttp
import backoff
from aiohttp import (
    InvalidURL,
    TooManyRedirects,
    ClientConnectorError,
    ServerDisconnectedError,
)
from bs4 import BeautifulSoup, Tag, NavigableString
from playwright._impl._api_types import TimeoutError
from playwright.async_api import async_playwright

from web.logger import get_logger
from web.models.product import Product
from web.models.store import Store, StoreSitemap

logger = get_logger(__name__)


class URLNotFound(Exception):
    pass


class ProductPriceNotFound(Exception):
    pass


class ProductNameNotFound(Exception):
    pass


class BaseScraper:
    @property
    def _random_user_agent(self):
        agents = [
            "Mozilla/5.0 (X11; Linux ppc64le; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/75.0",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 "
            "(KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
            "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/55.0.2919.83 Safari/537.36",
            "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) "
            "AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
        ]
        return choice(agents)

    async def get_through_simple_request(self, url, use_random_user_agent=True):
        headers = (
            {"User-Agent": self._random_user_agent} if use_random_user_agent else {}
        )
        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise URLNotFound(
                            f"Tried to get {url} but response was "
                            f"not successful {resp.status=}"
                        )

                    return await resp.text()
            except (
                InvalidURL,
                TooManyRedirects,
                ClientConnectorError,
                ServerDisconnectedError,
            ) as e:
                raise URLNotFound(f"Tried to get {url} the page was not found. ({e})")


class StoreScraper(BaseScraper):
    regex = r"(([A-Z]{3} )?(\$|€|£)?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})))"
    PRICE_PATTERN = re.compile(regex)

    def __init__(self, *, store: Store):
        self.store = store

    @backoff.on_exception(backoff.expo, TimeoutError, max_tries=3)
    async def get_through_browser(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(user_agent=self._random_user_agent)
            await page.goto(url)
            html = await page.content()
            await browser.close()
        return html

    async def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Get a soup object from an url"""
        html = (
            await self.get_through_simple_request(url)
            if not self.store.scrape_with_js
            else await self.get_through_browser(url)
        )
        return BeautifulSoup(html, "html.parser")

    def get_link(self, soup: BeautifulSoup) -> str:
        href = soup["href"] if soup.has_attr("href") else soup.find_next("a")["href"]
        if not href.startswith("http"):
            href = urljoin(self.store.website, href)
        return href

    def format_image_link(self, link: str) -> str:
        link = link.format(width=300)
        if link.startswith("//"):
            link = f"https:{link}"
        if not link.startswith("http"):
            link = f"{self.store.website}{link}"
        return link

    def parse_price(self, price_string: str) -> Optional[float]:
        match = self.PRICE_PATTERN.match(price_string)
        if match:
            locale.setlocale(locale.LC_NUMERIC, self.store.locale)
            return locale.atof(match.group(4))
        else:
            allowed_characters = string.digits + ".,$€£"
            clean_price = "".join(c for c in price_string if c in allowed_characters)
            return self.parse_price(clean_price)

    @staticmethod
    def remove_extra_spaces_and_newlines(value):
        value = re.sub(" +", " ", value)  # Remove extra spaces
        value = re.sub("\n{2,}", " ", value)  # Remove extra newlines
        value = re.sub("\x00", "", value)  # Remove NULL-terminated string
        return value.strip()

    def extract_product_availability(
        self, soup_obj: Union[Tag, NavigableString]
    ) -> bool:
        text = soup_obj.get_text().strip() if soup_obj else ""
        logger.debug(f"Found {text if soup_obj else 'nothing'} in availability tag")
        return bool(
            re.search(self.store.product_is_available_match.lower(), text.lower())
        )

    def extract_product_image(self, soup_obj: Union[Tag, NavigableString]) -> str:
        if soup_obj.name != "img":
            soup_obj = soup_obj.find("img")
        img_link = (
            soup_obj["data-src"] if soup_obj.has_attr("data-src") else soup_obj["src"]
        )
        return self.format_image_link(img_link)

    def extract_price(self, soup_obj: Union[Tag, NavigableString]) -> Optional[str]:
        unicode_str_text = self.remove_extra_spaces_and_newlines(soup_obj.get_text())
        try:
            return self.parse_price(unicode_str_text)
        except RecursionError:
            return

    async def scrape(self, url: str, fields: List[str]) -> Product:
        logger.debug(f"Scraping {fields} on {url}")
        soup = await self.get_soup(url)
        data = {}

        for field in fields:
            style_class = getattr(self.store, f"product_{field}_class")
            html_tag = getattr(self.store, f"product_{field}_tag")
            selector = (
                "class"
                if getattr(self.store, f"product_{field}_css_is_class")
                else "id"
            )

            if not bool(style_class) or not bool(html_tag):
                continue

            soup_obj = soup.find(html_tag, {selector: style_class})
            logger.debug(
                f"Scraping {field} with tag '{html_tag}' and {selector}='{style_class}'"
            )
            if not soup_obj:
                logger.warning(f"Nothing found when searching for {field}!")
                continue

            if field == "is_available":
                data[field] = self.extract_product_availability(soup_obj)
            elif field == "image":
                data[field] = self.extract_product_image(soup_obj)
            elif field == "price":
                data[field] = self.extract_price(soup_obj)
                data["currency"] = self.store.currency
            elif field == "variations" and not data.get("is_available", None):
                data["is_available"] = None
            elif field == "description":
                data[field] = soup_obj.get_text()
            else:
                data[field] = normalize(
                    "NFKD", self.remove_extra_spaces_and_newlines(soup_obj.get_text())
                )

        data.pop("variations", None)

        if not data.get("name"):
            raise ProductNameNotFound(
                f"Cannot create product without name: {url}; {data=}"
            )

        if not data.get("price"):
            raise ProductPriceNotFound(
                f"Cannot create product without price: {url}; {data=}"
            )

        data["id"] = f"{self.store.name}_{data.get('name')}".replace(" ", "_").replace(
            "\x00", ""
        )
        data["link"] = url
        return Product(**data)

    async def ping_website(self) -> Tuple[bool, Optional[str]]:
        try:
            await self.get_soup(self.store.website)
        except URLNotFound as e:
            return False, str(e)
        except Exception as e:
            msg = f"Unexpected error when pinging {self.store.name}: {e}"
            return False, msg

        return True, None


class SiteMapScraper(BaseScraper):
    async def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        xml = await self.get_through_simple_request(url, use_random_user_agent=False)
        return BeautifulSoup(xml, "xml")

    async def scrape(
        self,
        sitemap_urls: List[StoreSitemap],
        sort_by_last_modified: bool = True,
        limit: Optional[int] = None,
    ) -> List[str]:
        urls = []
        for sitemap in sitemap_urls:
            soup = await self.get_soup(sitemap.url)
            urls.extend(
                [
                    (
                        url.loc.text,
                        datetime.strptime(url.lastmod.text, sitemap.lastmod_format)
                        if url.lastmod
                        else datetime.utcnow(),
                    )
                    for url in soup.find_all("url")
                    if url.loc
                ]
            )
        if sort_by_last_modified:
            urls.sort(key=itemgetter(1), reverse=True)  # Last modified first

        links = [link for link, _ in urls]
        links_found = len(links)
        stop = limit if limit and limit < links_found else links_found
        return links[:stop]
