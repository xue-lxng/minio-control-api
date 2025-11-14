from typing import Optional

from pydantic import BaseModel


class CreateBucketResponse(BaseModel):
    bucket_name: str
    error: Optional[str] = None
