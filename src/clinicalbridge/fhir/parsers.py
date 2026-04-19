"""FHIR Resource Parsers - Convert FHIR resources to clean dicts"""

from datetime import datetime
from typing import Optional
import math


def parse_patient(patient_resource: dict) -> dict:
    """Parse FHIR Patient resource into clean dict."""
    if not patient_resource:
        return {}

    name = "Unknown"
    if patient_resource.get("name"):
        name_parts = patient_resource["name"][0]
        given = " ".join(name_parts.get("given", []))
        family = name_parts.get("family", "")
        name = f"{given} {family}".strip()

    dob = patient_resource.get("birthDate", "")
    age = calculate_age(dob) if dob else None
    gender = patient_resource.get("gender", "unknown")

    return {
        "patient_id": patient_resource.get("id", ""),
        "name": name,
        "dob": dob,
        "gender": gender,
        "age": age,
    }


def parse_medications(medications: list[dict]) -> list[dict]:
    """Parse FHIR MedicationRequest resources into clean list."""
    result = []
    for med in medications:
        med_text = med.get("medicationCodeableConcept", {}).get("coding", [{}])[0].get("display", "")
        if not med_text:
            med_text = med.get("medicationReference", {}).get("display", "Unknown")

        dosage = med.get("dosageInstruction", [{}])[0] if med.get("dosageInstruction") else {}
        dose_str = dosage.get("doseAndRate", [{}])[0].get("doseQuantity", {}) if dosage.get("doseAndRate") else {}
        dose_display = ""
        if dose_str:
            value = dose_str.get("value", "")
            unit = dose_str.get("unit", "")
            dose_display = f"{value}{unit}" if value else ""

        frequency = dosage.get("timing", {}).get("code", {}).get("coding", [{}])[0].get("display", "")
        frequency = frequency or dosage.get("text", "Unknown frequency")

        result.append({
            "name": med_text,
            "dose": dose_display or "Unknown dose",
            "frequency": frequency
        })

    return result


def parse_conditions(conditions: list[dict]) -> list[dict]:
    """Parse FHIR Condition resources into clean list."""
    result = []
    for cond in conditions:
        coding = cond.get("code", {}).get("coding", [{}])[0]
        display = cond.get("code", {}).get("text") or coding.get("display", "Unknown")
        icd10 = coding.get("code", "") if coding.get("system", "") == "http://hl7.org/fhir/sid/icd-10-cm" else ""

        result.append({
            "display": display,
            "icd10": icd10,
            "onset": cond.get("onsetDateTime", cond.get("onsetPeriod", {}).get("start", ""))[:7] if cond.get("onsetDateTime") else ""
        })

    return result


def parse_allergies(allergies: list[dict]) -> list[dict]:
    """Parse FHIR AllergyIntolerance resources into clean list."""
    result = []
    for allergy in allergies:
        substance = allergy.get("code", {}).get("text") or allergy.get("code", {}).get("coding", [{}])[0].get("display", "Unknown")
        reaction = "Unknown"
        if allergy.get("reaction"):
            reaction = allergy["reaction"][0].get("manifestation", [{}])[0].get("text") or \
                      allergy["reaction"][0].get("manifestation", [{}])[0].get("coding", [{}])[0].get("display", "Unknown reaction")

        severity = allergy.get("reaction", [{}])[0].get("severity", "unknown") if allergy.get("reaction") else "unknown"

        result.append({
            "substance": substance,
            "reaction": reaction,
            "severity": severity
        })

    return result


def calculate_age(dob: str) -> Optional[int]:
    """Calculate age from date of birth string (YYYY-MM-DD)."""
    try:
        birth_date = datetime.strptime(dob, "%Y-%m-%d")
        today = datetime.now()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except (ValueError, AttributeError):
        return None
