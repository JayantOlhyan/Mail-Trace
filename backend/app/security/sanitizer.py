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

    # 1. Remove dangerous HTML tags and clean attributes in one pass
    for tag in soup.find_all(True):
        tag_name_lower = tag.name.lower()
        if any(bad_tag in tag_name_lower for bad_tag in FORBIDDEN_TAGS):
            tag.decompose()
            continue

        # 2. Clean dangerous attributes from remaining tags
        attrs_to_remove = []
        for attr, value in tag.attrs.items():
            attr_lower = attr.lower()
            val_str = str(value).lower()
            
            # Remove all whitespace and common encoded entities to catch obfuscated "javascript:"
            val_clean = re.sub(r'[\s\x00-\x1f\x7f]+', '', val_str)
            val_clean = val_clean.replace("&colon;", ":").replace("&#58;", ":")
            
            if attr_lower.startswith("on") or "javascript:" in val_clean or "vbscript:" in val_clean:
                attrs_to_remove.append(attr)

        for attr in attrs_to_remove:
            del tag[attr]

    return str(soup)
