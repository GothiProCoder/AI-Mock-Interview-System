from pydantic import BaseModel, Field
from typing import List, Literal

class PerformanceSnippet(BaseModel):
    topic: str = Field(description="The specific technical or behavioral topic")
    quote: str = Field(description="A brief, verbatim quote from the candidate")
    assessment: str = Field(description="A concise, neutral assessment of the response")
    type: Literal['positive', 'negative', 'neutral'] = Field(description="Sentiment of the performance")

class AnalysisReport(BaseModel):
    snippets: List[PerformanceSnippet] = Field(description="List of extracted performance snippets")

class CandidateSummary(BaseModel):
    headline: str = Field(description="A single, impactful sentence summarizing the candidate")
    overall_impression: str = Field(description="A 2-3 sentence paragraph with overall impression")

class StrengthInsight(BaseModel):
    skill: str = Field(description="The high-level skill or competency identified")
    evidence: str = Field(description="Evidence from transcript supporting this strength")

class WeaknessInsight(BaseModel):
    skill: str = Field(description="The high-level area for development")
    evidence: str = Field(description="Evidence from transcript supporting this weakness")
    priority: Literal['High', 'Medium', 'Low'] = Field(description="Priority to address")

class Insights(BaseModel):
    strengths: List[StrengthInsight]
    weaknesses: List[WeaknessInsight]

class RoadmapStep(BaseModel):
    timespan: str = Field(description="Timeframe for this step, e.g., 'Day 1-5'")
    focus: str = Field(description="Primary theme or goal for this period")
    activities: List[str] = Field(description="List of concrete, actionable tasks")

class RecommendedResource(BaseModel):
    topic: str = Field(description="The topic this resource relates to")
    link: str = Field(description="The direct URL to the resource")
    reason: str = Field(description="Why this specific resource is recommended")

class DevelopmentPlan(BaseModel):
    priority_topics: List[str] = Field(description="Most critical topics to focus on")
    roadmap_2_weeks: List[RoadmapStep]
    recommended_resources: List[RecommendedResource]

class FinalReport(BaseModel):
    candidate_summary: CandidateSummary
    insights: Insights
    development_plan: DevelopmentPlan
