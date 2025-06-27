from pydantic import BaseModel
from typing import Optional


class ScrapeRequest(BaseModel): #RRB JE
    url: Optional[str] = None
    category: Optional[str] = None
    Horizontalcategory: Optional[str] = None
    Exam_Language: Optional[str] = None
    rrb_zone: Optional[str] = None
    RRB_branch: Optional[str] = None,
    exam_type: Optional[str] = None,
    password:Optional[str] = None
