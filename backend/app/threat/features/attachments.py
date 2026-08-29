from typing import List, Dict, Any
from app.schemas.canonical import CanonicalEmailObject

class AttachmentFeatureExtractor:
    """
    Extracts risk signals from attachment metadata:
    - Double extensions (e.g. invoice.pdf.exe)
    - Executable MIME types and extensions (.exe, .scr, .bat, .vbs, .ps1, .js, .iso)
    - Archive extensions (.zip, .rar, .7z, .iso)
    """

    EXECUTABLE_EXTENSIONS = [".exe", ".scr", ".bat", ".cmd", ".vbs", ".ps1", ".js", ".hta", ".wsf", ".cpl"]
    ARCHIVE_EXTENSIONS = [".zip", ".rar", ".7z", ".iso", ".img", ".tar", ".gz"]

    @classmethod
    def extract_features(cls, canonical_email: CanonicalEmailObject) -> Dict[str, Any]:
        attachments = canonical_email.attachments

        has_executable = False
        has_double_extension = False
        has_archive = False
        suspicious_attachments: List[str] = []

        for att in attachments:
            fname = att.filename.lower()

            # Double extension check (e.g. invoice.pdf.exe)
            parts = fname.split(".")
            if len(parts) >= 3 and f".{parts[-1]}" in cls.EXECUTABLE_EXTENSIONS:
                has_double_extension = True
                suspicious_attachments.append(att.filename)

            # Executable extension check
            if any(fname.endswith(ext) for ext in cls.EXECUTABLE_EXTENSIONS) or "executable" in att.mime_type:
                has_executable = True
                suspicious_attachments.append(att.filename)

            # Archive check
            if any(fname.endswith(ext) for ext in cls.ARCHIVE_EXTENSIONS) or "zip" in att.mime_type or "compressed" in att.mime_type:
                has_archive = True

        return {
            "attachment_count": len(attachments),
            "has_executable": has_executable,
            "has_double_extension": has_double_extension,
            "has_archive": has_archive,
            "suspicious_attachments": list(set(suspicious_attachments))
        }
