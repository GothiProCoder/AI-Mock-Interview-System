import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

from pipeline.pipeline import InterviewAnalysisPipeline
from pipeline.models import FinalReport

# Define the request body model
class AnalysisRequest(BaseModel):
    metadata: Dict[str, Any] = Field(..., example={"candidate_id": "C-EDGE-01"})
    transcript: Dict[str, str] = Field(..., example={"interviewer": "Hello", "candidate": "Hi"})

# Initialize the FastAPI app
app = FastAPI(
    title="Interview Analysis API",
    description="An API for analyzing interview transcripts.",
    version="1.0.0"
)

# Load the pipeline
# This is done once at startup to avoid reloading the model on every request
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable not set.")

pipeline = InterviewAnalysisPipeline(api_key=api_key)

@app.post("/analyze", response_model=FinalReport)
async def analyze_interview(request: AnalysisRequest):
    """
    Analyzes an interview transcript and returns a comprehensive report.
    """
    try:
        # The pipeline's analyze method expects a dictionary with 'metadata' and 'transcript' keys,
        # which matches our AnalysisRequest model.
        report = pipeline.analyze(request.dict())
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # A generic error handler for any other exceptions
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
