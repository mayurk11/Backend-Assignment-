from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ImageInput(BaseModel):
    image_url: str
    
class VisitInput(BaseModel):
    store_id: str
    image_url: List[str]
    visit_time: datetime

class SubmitJobRequest(BaseModel):
    count: int
    visits: List[VisitInput]

    # custom validation
    def validate_count(self):
        if self.count != len(self.visits):
            raise ValueError("count must match number of visits")

class SubmitJobResponse(BaseModel):
    job_id: int
    
class JobStatusResponse(BaseModel):
    status: str
    job_id: int
    error: Optional[List[dict]] = None
    
class VisitData(BaseModel):
    date: datetime
    perimeter: float
    
class VisitResult(BaseModel):
    store_id: str
    area: str
    store_name: str
    data: List[VisitData]
    
class VisitReportResponse(BaseModel):
    results: List[VisitResult]