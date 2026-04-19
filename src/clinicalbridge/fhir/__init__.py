"""FHIR R4 Client for Healthcare Data Access"""

import httpx
from typing import Optional


class FHIRClient:
    """Async FHIR R4 client for querying healthcare resources."""

    def __init__(self, base_url: str, token: Optional[str] = None):
        """
        Initialize FHIR client.

        Args:
            base_url: FHIR server base URL (e.g., https://r4.smarthealthit.org)
            token: Optional Bearer token for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json"
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    async def get_patient(self, patient_id: str) -> dict:
        """Fetch Patient resource from FHIR server."""
        clean_id = patient_id.replace("Patient/", "")
        url = f"{self.base_url}/Patient/{clean_id}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_medications(self, patient_id: str) -> list[dict]:
        """Fetch active MedicationRequest resources for a patient."""
        clean_id = patient_id.replace("Patient/", "")
        url = f"{self.base_url}/MedicationRequest"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                url,
                headers=self.headers,
                params={"patient": clean_id, "status": "active", "_count": 50}
            )
            resp.raise_for_status()
            bundle = resp.json()
            return [e["resource"] for e in bundle.get("entry", [])]

    async def get_conditions(self, patient_id: str) -> list[dict]:
        """Fetch active Condition resources for a patient."""
        clean_id = patient_id.replace("Patient/", "")
        url = f"{self.base_url}/Condition"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                url,
                headers=self.headers,
                params={"patient": clean_id, "_count": 50}
            )
            resp.raise_for_status()
            bundle = resp.json()
            return [e["resource"] for e in bundle.get("entry", [])]

    async def get_allergies(self, patient_id: str) -> list[dict]:
        """Fetch AllergyIntolerance resources for a patient."""
        clean_id = patient_id.replace("Patient/", "")
        url = f"{self.base_url}/AllergyIntolerance"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                url,
                headers=self.headers,
                params={"patient": clean_id, "_count": 50}
            )
            resp.raise_for_status()
            bundle = resp.json()
            return [e["resource"] for e in bundle.get("entry", [])]

    async def search(self, resource_type: str, params: dict) -> dict:
        """Generic search on any resource type."""
        url = f"{self.base_url}/{resource_type}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
