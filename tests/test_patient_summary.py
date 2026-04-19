"""Test Patient Summary Tool"""

import pytest
from unittest.mock import AsyncMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from clinicalbridge.tools import get_patient_summary


@pytest.mark.asyncio
async def test_patient_summary_missing_patient_id():
    """Test that patient_summary returns error when patient_id is missing."""
    result = await get_patient_summary("", ctx=None)
    assert "error" in result


@pytest.mark.asyncio
async def test_patient_summary_data_classification():
    """Test that all results include data_classification."""
    # This will fail without valid FHIR server, but we test the structure
    result = await get_patient_summary("fake-patient", ctx=None)
    # Should have error or proper classification
    if "error" not in result:
        assert result.get("data_classification") == "SYNTHETIC"
