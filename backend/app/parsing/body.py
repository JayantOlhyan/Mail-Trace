import email
from typing import Tuple, Optional

class BodyExtractor:
    """
    Extracts text/plain and text/html body streams from MIME email payloads.
    Preserves original HTML and text content intact without executing scripts or stripping markup.
    """

    @classmethod
    def extract_body(cls, msg: email.message.EmailMessage) -> Tuple[str, Optional[str]]:
        text_body = ""
        html_body: Optional[str] = None

        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                filename = part.get_filename()

                # Ignore attachments
                if filename or "attachment" in content_disposition.lower():
                    continue

                content_type = part.get_content_type()
                if content_type == "text/plain" and not text_body:
                    text_body = cls._decode_part(part)
                elif content_type == "text/html" and not html_body:
                    html_body = cls._decode_part(part)
        else:
            content_type = msg.get_content_type()
            decoded_text = cls._decode_part(msg)
            if content_type == "text/html":
                html_body = decoded_text
            else:
                text_body = decoded_text

        return text_body.strip(), html_body

    @classmethod
    def _decode_part(cls, part: email.message.EmailMessage) -> str:
        payload = part.get_payload(decode=True)
        if not payload:
            return ""

        charset = part.get_content_charset() or "utf-8"
        try:
            return payload.decode(charset, errors="replace")
        except (LookupError, UnicodeDecodeError):
            return payload.decode("latin1", errors="replace")
