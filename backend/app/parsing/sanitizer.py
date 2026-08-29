import re
from bs4 import BeautifulSoup

class HTMLSanitizer:
    """
    Sanitizes HTML content from email bodies.
    Strips executable scripts, iframes, object embeds, event handlers, and javascript URIs
    while preserving clean readable markup and hyperlinked URLs for threat inspection.
    """

    DANGEROUS_TAGS = {"script", "iframe", "embed", "object", "applet", "form", "input", "button", "meta", "link", "style"}
    DANGEROUS_ATTR_PATTERNS = [re.compile(r"^on", re.I), re.compile(r"^javascript:", re.I)]

    @classmethod
    def sanitize(cls, html_content: str) -> str:
        if not html_content or not html_content.strip():
            return ""

        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Remove dangerous tags completely
        for tag_name in cls.DANGEROUS_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # 2. Strip inline event handlers (onload, onclick) and javascript: URLs
        for tag in soup.find_all(True):
            attrs_to_remove = []
            for attr, val in tag.attrs.items():
                # Check for inline event handler (e.g. onload)
                if attr.lower().startswith("on"):
                    attrs_to_remove.append(attr)
                # Check for javascript: pseudo-protocol in href/src
                elif attr.lower() in ("href", "src", "action"):
                    val_str = str(val).strip()
                    if re.match(r"^javascript:", val_str, re.I) or re.match(r"^data:text/html", val_str, re.I):
                        attrs_to_remove.append(attr)

            for attr in attrs_to_remove:
                del tag.attrs[attr]

        return str(soup)

    @classmethod
    def extract_urls(cls, html_content: str, text_content: str) -> list[str]:
        """Extracts unique URLs from both HTML markup and plain text body."""
        urls = set()
        
        # Regex pattern for extracting HTTP/HTTPS URLs
        url_regex = re.compile(
            r'https?://[^\s<>"]+|www\.[^\s<>"]+', re.IGNORECASE
        )

        if text_content:
            for match in url_regex.findall(text_content):
                urls.add(match.rstrip(".,;)'\""))

        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href.startswith("http://") or href.startswith("https://"):
                    urls.add(href)
            
            for match in url_regex.findall(html_content):
                urls.add(match.rstrip(".,;)'\""))

        return sorted(list(urls))
