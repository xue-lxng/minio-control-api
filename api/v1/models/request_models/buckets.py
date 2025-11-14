from fastapi.params import Body
from pydantic import BaseModel, field_validator


class CreateBucketRequest(BaseModel):
    bucket_name: str = Body(..., description="Bucket name")

    @field_validator("bucket_name")
    def bucket_name_does_not_contain_unprocessable_characters(cls, v: str) -> str:
        if any(char in v for char in ".,!@#$%^&*()_+={}[]|\\:;\"'<>?/"):
            raise ValueError("bucket_name cannot contain unprocessable characters")
        return v
