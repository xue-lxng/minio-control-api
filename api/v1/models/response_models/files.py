from typing import Optional

from pydantic import BaseModel


class GetLinkResponseModel(BaseModel):
    link: str
    error: Optional[str] = None
