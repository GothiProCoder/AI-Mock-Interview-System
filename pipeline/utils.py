from typing import Dict, Tuple, Optional, Union
from pipeline.models import FinalReport

def format_transcript(transcript_obj: Union[Dict[str, str], Dict]) -> str:
    """
    Format interview transcript with intelligent sorting.
    Handles both flat dict and nested dict with 'transcript' key.
    """
    # Handle nested structure with metadata
    if "transcript" in transcript_obj:
        transcript_obj = transcript_obj["transcript"]
    
    def sort_key(k):
        if "interviewer" in k.lower():
            return (0, k)
        elif "candidate" in k.lower():
            return (1, k)
        else:
            return (2, k)
    
    sorted_keys = sorted(transcript_obj.keys(), key=sort_key)
    lines = []
    for key in sorted_keys:
        role = "Interviewer" if "interviewer" in key.lower() else "Candidate"
        lines.append(f"{role}: {transcript_obj[key]}")
    return "\n\n".join(lines)


def validate_transcript(transcript_obj: Union[Dict[str, str], Dict]) -> Tuple[bool, Optional[str]]:
    """
    Validate transcript structure and content.
    Handles both flat dict and nested dict with 'transcript' key.
    """
    # Handle nested structure with metadata
    if "transcript" in transcript_obj:
        transcript_obj = transcript_obj["transcript"]
    
    if not transcript_obj:
        return False, "Transcript cannot be empty"
    if len(transcript_obj) < 2:
        return False, "Transcript must have at least 2 exchanges"
    
    has_interviewer = any('interviewer' in k.lower() for k in transcript_obj.keys())
    has_candidate = any('candidate' in k.lower() for k in transcript_obj.keys())
    
    if not has_interviewer:
        return False, "Transcript must include interviewer questions"
    if not has_candidate:
        return False, "Transcript must include candidate responses"
    
    for key, value in transcript_obj.items():
        if not value or not value.strip():
            return False, f"Entry '{key}' is empty"
    
    return True, None


def validate_report_quality(report: FinalReport) -> Tuple[bool, list[str]]:
    """Validate the quality of generated report."""
    issues = []
    if len(report.candidate_summary.headline) < 20:
        issues.append("Headline is too short/generic")
    if len(report.candidate_summary.overall_impression) < 50:
        issues.append("Overall impression lacks detail")
    if len(report.insights.strengths) == 0:
        issues.append("No strengths identified")
    if len(report.insights.weaknesses) == 0:
        issues.append("No weaknesses identified")
    if len(report.development_plan.priority_topics) == 0:
        issues.append("No priority topics defined")
    if len(report.development_plan.roadmap_2_weeks) < 2:
        issues.append("2-week roadmap insufficiently detailed")
    if len(report.development_plan.recommended_resources) == 0:
        issues.append("No learning resources provided")
    for resource in report.development_plan.recommended_resources:
        if not resource.link or not resource.link.strip():
            issues.append(f"Resource '{resource.topic}' has empty link")
        elif not (resource.link.startswith('http://') or resource.link.startswith('https://')):
            issues.append(f"Resource '{resource.topic}' has invalid link format")
    return (len(issues) == 0), issues
