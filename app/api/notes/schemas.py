from pydantic import BaseModel, Field
from api.base.base_schemas import BaseResponse, PaginationParams
from models.notes import NotesSchema

class NotesRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=6, max_length=500)

class NotesResponse(BaseResponse):
    data: dict | None

class ReadNotesResponse(BaseResponse):
    data: dict | None

class ReadAllNotesRequest(PaginationParams):
    include_deleted: bool = False
    filter_user: bool = True

class ReadAllNotesResponse(BaseResponse):
    data: dict | None

class UpdateNotesRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=6, max_length=500)

class UpdateNotesResponse(BaseResponse):
    data: dict | None

class DeleteNotesResponse(BaseResponse):
    data: dict | None