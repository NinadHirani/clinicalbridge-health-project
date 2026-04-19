"""SHARP Context Extraction

SHARP (Standardized Healthcare Agent Runtime Parameters) context propagation
for Prompt Opinion MCP integration. Supports both ctx.meta dict and HTTP headers.
"""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class SHARPContext:
    """SHARP context fields for healthcare agent runtime."""

    patient_id: str = ""
    fhir_base_url: str = ""
    fhir_access_token: str = ""
    encounter_id: str = ""
    practitioner_id: str = ""
    organization_id: str = ""

    def __post_init__(self):
        # Fallback to environment variables if not set
        if not self.fhir_base_url:
            self.fhir_base_url = os.getenv("FHIR_BASE_URL", "https://r4.smarthealthit.org")
        if not self.fhir_access_token:
            self.fhir_access_token = os.getenv("FHIR_TOKEN", "")


def extract_sharp(ctx) -> SHARPContext:
    """
    Extract SHARP context from FastMCP Context.
    Checks in order: ctx.meta["sharp"] dict → HTTP request headers → env vars.

    Args:
        ctx: FastMCP Context object (can be None)

    Returns:
        SHARPContext object with resolved values
    """
    if ctx is None:
        return SHARPContext()

    # First, try to extract from ctx.meta dict (MCP standard)
    meta = getattr(ctx, "meta", {}) or {}
    sharp_raw = meta.get("sharp", {}) or {}

    # Also check HTTP headers (Prompt Opinion forwards SHARP as headers)
    headers: dict = {}
    request = getattr(ctx, "request", None)
    if request:
        raw_headers = getattr(request, "headers", {})
        headers = {k.lower(): v for k, v in dict(raw_headers).items()}

    def _get(meta_key: str, header_key: str, default: str = "") -> str:
        """Get value from meta dict, then headers, then default."""
        return (
            sharp_raw.get(meta_key)
            or headers.get(header_key.lower())
            or default
        )

    return SHARPContext(
        patient_id=_get("patient_id", "x-sharp-patient-id"),
        fhir_base_url=_get("fhir_base_url", "x-sharp-fhir-url"),
        fhir_access_token=_get("fhir_access_token", "x-sharp-fhir-token"),
        encounter_id=_get("encounter_id", "x-sharp-encounter-id"),
        practitioner_id=_get("practitioner_id", "x-sharp-practitioner-id"),
        organization_id=_get("organization_id", "x-sharp-organization-id"),
    )
