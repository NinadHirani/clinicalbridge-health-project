"""Synthetic Data Generators for Testing and Demos"""

import random
from datetime import datetime, timedelta


def generate_follow_up_slots(
    specialty: str,
    zip_code: str,
    days_from_now: int = 14
) -> list[dict]:
    """Generate realistic synthetic appointment slots."""

    providers = {
        "endocrinology": ["Dr. Maria Chen, MD", "Dr. James Okafor, MD", "Dr. Priya Nair, DO"],
        "cardiology": ["Dr. Robert Kim, MD", "Dr. Sarah Patel, MD"],
        "primary_care": ["Dr. Lisa Torres, MD", "Dr. Alan Johnson, DO", "Dr. Wei Zhang, MD"],
        "nephrology": ["Dr. Fatima Al-Hassan, MD"],
        "pulmonology": ["Dr. Carlos Rivera, MD", "Dr. Emily Park, MD"],
    }

    specialty_lower = specialty.lower().replace(" ", "_")
    provider_list = providers.get(specialty_lower, providers["primary_care"])

    slots = []
    base_date = datetime.now()

    # Use zip code and specialty for deterministic seeding
    random.seed(int(zip_code[:3] or "0") + hash(specialty) % 1000)

    for i, provider in enumerate(provider_list[:3]):
        offset_days = random.randint(2, days_from_now)
        slot_date = base_date + timedelta(days=offset_days)
        hour = random.choice([9, 10, 11, 14, 15])
        minute = random.choice([0, 30])

        slots.append({
            "slot_id": f"slot-{hash(provider+zip_code) % 10000:04x}",
            "provider": provider,
            "facility": f"{'Telehealth' if i == 0 else 'Regional'} {specialty.title()} Associates",
            "date": slot_date.strftime("%Y-%m-%d"),
            "time": f"{hour}:{minute:02d} {'AM' if hour < 12 else 'PM'}",
            "type": "Telehealth" if i == 0 else "In-person",
            "distance_miles": 0 if i == 0 else round(random.uniform(0.5, 8.0), 1),
            "accepting_new_patients": True
        })

    return slots
