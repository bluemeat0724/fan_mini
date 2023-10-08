import json
from typing import Optional, Union, Dict, Any

import typing
from pydantic import BaseModel, Field, model_validator
from json import JSONEncoder
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask


class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.strftime('%Y-%m-%d %H:%M:%S')


class JsonResponse(BaseModel):
    success: bool = True
    data: Any = {}
    error_msg: str = ''
    code: int = 0


class StructuredResponse(JSONResponse):

    def __init__(
            self,
            content: typing.Any,
            status_code: int = 200,
            success: bool = True,
            headers: typing.Optional[typing.Dict[str, str]] = None,
            media_type: typing.Optional[str] = None,
            background: typing.Optional[BackgroundTask] = None,
    ) -> None:
        if success:
            content = JsonResponse(success=success, data=content).model_dump()
        else:
            content = JsonResponse(success=success, error_msg=content, code=status_code).model_dump()
        super().__init__(content, status_code, headers, media_type, background)


class PaginationResponse(BaseModel):
    total: int
    page_no: int
    page_size: int
    total_page: Optional[int] = Field(default=None, validate_default=True)
    items: Any = {}

    @model_validator(mode='after')
    def set_total_page(cls, values):
        values.total_page = values.total // values.page_size + 1 if values.total_page is None else values.total_page





