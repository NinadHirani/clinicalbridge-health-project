"""SHARP Context Extraction

SHARP (Standardized Healthcare Agent Runtime Parameters) context propagation
for Prompt Opinion MCP integration.
"""

from dataclasses import dataclass, field
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
    Extract SHARP context from FastMCP Context.meta dict.
    Falls back to environment variables for local testing.

    Args:
        ctx: FastMCP Context object (can be None)

    Returns:
        SHARPContext object with resolved values
    """
    if ctx is None:
        return SHARPContext()

    meta = getattr(ctx, "meta", {}) or {}
    sharp_raw = meta.get("sharp", {}) or {}

    return SHARPContext(
        patient_id=sharp_raw.get("patient_id", ""),
        fhir_base_url=sharp_raw.get("fhir_base_url", ""),
        fhir_access_token=sharp_raw.get("fhir_access_token", ""),
        encounter_id=sharp_raw.get("encounter_id", ""),
        practitioner_id=sharp_raw.get("practitioner_id", ""),
        organization_id=sharp_raw.get("organization_id", ""),
    )
