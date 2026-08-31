import re
from bs4 import BeautifulSoup

FORBIDDEN_TAGS = ["script", "iframe", "object", "embed", "applet", "form", "input", "button", "meta", "link", "base"]
FORBIDDEN_ATTRIBUTES = ["onload", "onerror", "onclick", "onmouseover", "onfocus", "onblur", "onkeydown", "javascript:"]


def sanitize_email_html(html_content: str) -> str:
    """
    Sanitizes raw untrusted email HTML content to prevent XSS and script injection.
    Strips forbidden tags, inline scripts, event handlers, and javascript: URIs.
    """
    if not html_content or not isinstance(html_content, str):
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Remove dangerous HTML tags
    for tag in soup.find_all(FORBIDDEN_TAGS):
        tag.decompose()

    # 2. Clean dangerous attributes from remaining tags
    for tag in soup.find_all(True):
        attrs_to_remove = []
        for attr, value in tag.attrs.items():
            attr_lower = attr.lower()
            val_lower = str(value).lower()
            if attr_lower.startswith("on") or "javascript:" in val_lower:
                attrs_to_remove.append(attr)

        for attr in attrs_to_remove:
            del tag[attr]

    return str(soup)
