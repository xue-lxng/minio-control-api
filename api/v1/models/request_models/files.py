from fastapi.params import Body
from pydantic import field_validator, BaseModel
import os
from typing import ClassVar, Set

class GetImageLinkRequestModel(BaseModel):
    project_id: str = Body(..., description='Project ID')
    file_path: str = Body(..., description='File path (must be an image file, e.g. "image.png")')
    placeholder_if_not_found: bool = Body(False, description='Placeholder if file not found')

    _image_exts: ClassVar[Set[str]] = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.svg'}

    @field_validator('file_path')
    def file_path_must_be_image(cls, v: str) -> str:
        _, ext = os.path.splitext(v or '')
        if not ext or ext.lower() not in cls._image_exts:
            raise ValueError('file_path must be an image file')
        return v