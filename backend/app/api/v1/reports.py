from fastapi import APIRouter, HTTPException, status, Response, Query
from app.reports.demo import sih_demo_service
from app.reports.exporter import ReportExporter
from app.schemas.reports import ForensicReportSchema

router = APIRouter(tags=["Forensic Reports & Evidence Export"])
exporter = ReportExporter()


@router.post("/cases/{case_id}/reports", response_model=ForensicReportSchema)
async def generate_case_report(case_id: str, version: str = Query("1.0")):
    """
    Generates a structured ForensicReportSchema from a case across Phases 1-6.
    """
    report = sih_demo_service.get_demo_report(case_id=case_id)
    report.version = version
    return report


@router.get("/reports/{report_id}", response_model=ForensicReportSchema)
async def get_report_detail(report_id: str):
    """
    Fetches structured forensic report metadata and findings by report ID.
    """
    case_id = report_id.replace("RPT-", "CASE-") if report_id.startswith("RPT-") else f"CASE-{report_id}"
    return sih_demo_service.get_demo_report(case_id=case_id)


@router.get("/reports/{report_id}/pdf")
async def download_report_pdf(report_id: str):
    """
    Downloads printable PDF forensic report.
    """
    case_id = report_id.replace("RPT-", "CASE-") if report_id.startswith("RPT-") else f"CASE-{report_id}"
    report = sih_demo_service.get_demo_report(case_id=case_id)
    pdf_bytes = exporter.export_pdf(report)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{report_id}.pdf"'
        },
    )


@router.get("/reports/{report_id}/json")
async def download_report_json(report_id: str):
    """
    Downloads machine-readable JSON forensic report.
    """
    case_id = report_id.replace("RPT-", "CASE-") if report_id.startswith("RPT-") else f"CASE-{report_id}"
    report = sih_demo_service.get_demo_report(case_id=case_id)
    json_str = exporter.export_json(report)

    return Response(
        content=json_str,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{report_id}.json"'
        },
    )


@router.get("/reports/{report_id}/package")
async def download_evidence_package(report_id: str):
    """
    Downloads ZIP Evidence Package with manifest.json and SHA-256 checksums.
    """
    case_id = report_id.replace("RPT-", "CASE-") if report_id.startswith("RPT-") else f"CASE-{report_id}"
    report = sih_demo_service.get_demo_report(case_id=case_id)
    zip_bytes = exporter.export_zip_package(report)

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="ThreatTrace-AI-Evidence-{report_id}.zip"'
        },
    )


@router.post("/demo/reset")
async def reset_demo_environment():
    """
    Resets the SIH demonstration environment to baseline state.
    """
    sih_demo_service.reset_demo_data()
    return {"status": "SUCCESS", "message": "SIH Demo environment reset to baseline."}
