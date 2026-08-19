from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class Difficulty(str,Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

class ProblemCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100, description="Problem title")
    description: str = Field(min_length=10, max_length=10000, description="Detailed problem statement")
    difficulty: Difficulty = Field(description="Difficulty level")
    constraints: Optional[str] = Field(default=None, max_length=2000, description="Problem constraints")
    input_format: Optional[str] = Field(default=None, max_length=2000, description="Input format description")
    output_format: Optional[str] = Field(default=None, max_length=2000, description="Output format description")

class ProblemResponse(BaseModel):
    problem_id:int
    title:str
    description:str
    difficulty:Difficulty
    constraints: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None