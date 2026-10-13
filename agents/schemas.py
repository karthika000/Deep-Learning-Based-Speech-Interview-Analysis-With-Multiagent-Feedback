from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ModelPredictions(BaseModel):
    speaking_skills: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    interview_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    overall_performance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    answer_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class AcousticFeatures(BaseModel):
    duration_sec: Optional[float] = None
    speaking_rate_wpm: Optional[float] = None
    pause_count: Optional[int] = None
    long_pause_count: Optional[int] = None
    pause_ratio: Optional[float] = None
    mean_pitch: Optional[float] = None
    pitch_variation: Optional[float] = None
    mean_energy: Optional[float] = None


class ModelOutput(BaseModel):
    sample_id: str
    question: str
    transcript: str
    predictions: ModelPredictions
    acoustic_features: AcousticFeatures


class AgentResult(BaseModel):
    agent_name: str
    response: str


class FinalFeedback(BaseModel):
    sample_id: str
    overall_summary: str
    strengths: List[str]
    areas_to_improve: List[str]
    actionable_suggestions: List[str]
    next_practice_task: str
    safety_note: str
    agent_discussion: Dict[str, str]