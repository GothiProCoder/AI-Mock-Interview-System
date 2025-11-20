import pytest
from fastapi.testclient import TestClient
from main import app
from pipeline.pipeline import InterviewAnalysisPipeline
from pipeline.models import FinalReport, CandidateSummary, Insights, DevelopmentPlan

# Create a TestClient instance
client = TestClient(app)

# Mock data for testing
mock_request_data = {
    "metadata": {"candidate_id": "C-TEST-01"},
    "transcript": {"interviewer": "Hello", "candidate": "Hi"},
}

mock_final_report = FinalReport(
    candidate_summary=CandidateSummary(headline="Test Headline", overall_impression="Test Impression"),
    insights=Insights(strengths=[], weaknesses=[]),
    development_plan=DevelopmentPlan(priority_topics=[], roadmap_2_weeks=[], recommended_resources=[])
)

def test_analyze_success(monkeypatch):
    """
    Test the /analyze endpoint for a successful response.
    """
    # Mock the analyze method of the InterviewAnalysisPipeline
    def mock_analyze(*args, **kwargs):
        return mock_final_report

    monkeypatch.setattr(InterviewAnalysisPipeline, "analyze", mock_analyze)

    response = client.post("/analyze", json=mock_request_data)
    assert response.status_code == 200
    assert response.json()["candidate_summary"]["headline"] == "Test Headline"

def test_analyze_value_error(monkeypatch):
    """
    Test the /analyze endpoint for a ValueError, expecting a 400 response.
    """
    # Mock the analyze method to raise a ValueError
    def mock_analyze_error(*args, **kwargs):
        raise ValueError("Invalid transcript")

    monkeypatch.setattr(InterviewAnalysisPipeline, "analyze", mock_analyze_error)

    response = client.post("/analyze", json=mock_request_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid transcript"

def test_analyze_internal_error(monkeypatch):
    """
    Test the /analyze endpoint for a generic exception, expecting a 500 response.
    """
    # Mock the analyze method to raise a generic Exception
    def mock_analyze_internal_error(*args, **kwargs):
        raise Exception("Something went wrong")

    monkeypatch.setattr(InterviewAnalysisPipeline, "analyze", mock_analyze_internal_error)

    response = client.post("/analyze", json=mock_request_data)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json()["detail"]
    