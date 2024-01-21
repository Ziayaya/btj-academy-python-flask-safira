import datetime
import math

from sqlalchemy import select, func
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import HTTPException

from db import get_session
from api.base.base_schemas import PaginationMetaResponse, PaginationParams
from models.notes import Notes, NotesSchema
from .schemas import (
    NotesRequest,
    UpdateNotesRequest
)

class NewNotes:
    def __init__(self) -> None:
        self.session = get_session()

    def execute(self, user_id, request: NotesRequest) -> NotesSchema:
        with self.session as session:
            notes = session.execute(
                select(Notes).where(Notes.created_by == user_id)
            )
            notes = notes.scalars().first()

            notes = Notes()
            notes.title = request.title
            notes.content = request.content
            notes.created_at = datetime.datetime.utcnow()
            notes.updated_at = datetime.datetime.utcnow()
            notes.created_by = user_id
            notes.updated_by = user_id

            session.add(notes)
            session.flush()

            return NotesSchema.from_orm(notes)

class GetOneNote:
    def __init__(self) -> None:
        self.session = get_session()

    def execute(self, note_id, user_id) -> NotesSchema:
        with self.session as session:
            # Retrieve a single note by its ID and ensure it belongs to the specified user
            note = session.execute(
                select(Notes).where(
                    (Notes.note_id == note_id).__and__(Notes.created_by == user_id).__and__(Notes.deleted_at == None)
                )
            ).scalars().first()
            if not note:
                exception = HTTPException(description="notes not found")
                exception.code = 404
                raise exception
            return NotesSchema.from_orm(note)
        
class ReadAllNote:
    def __init__(self) -> None:
        self.session = get_session()
    def execute(self, user_id: int, page_params: PaginationParams, include_deleted: bool, filter_user: bool) -> (list[dict], PaginationMetaResponse):
        with self.session as session:
            total_item = session.execute(
                select(func.count())
                .select_from(Notes).where(
                    (Notes.created_by == user_id) & (Notes.deleted_at == None)
                )
            ).scalar()

            query = (
                select(Notes)
                .offset((page_params.page-1) * page_params.item_per_page)
                .limit(page_params.item_per_page)
            )

            if filter_user:
                query = query.filter(Notes.created_by == user_id)

            if not include_deleted:
                query = query.filter(Notes.deleted_at == None)

            paginated_query = session.execute(query).scalars().all()

            notes = [NotesSchema.from_orm(p).__dict__ for p in paginated_query]

            meta = PaginationMetaResponse(
                total_item=total_item,
                page=page_params.page,
                item_per_page=page_params.item_per_page,
                total_page=math.ceil(total_item / page_params.item_per_page)
            )

            return notes, meta
        
class UpdateNote:
    def __init__(self) -> None:
        self.session = get_session()

    def execute(self, note_id, user_id, request: UpdateNotesRequest ) -> NotesSchema:
        with self.session as session:
            # Retrieve the note by its ID and ensure it belongs to the specified user
            note = session.execute(
                select(Notes).where(
                    (Notes.note_id == note_id).__and__(Notes.created_by == user_id).__and__(Notes.deleted_at == None)
                )
            )
            note = note.scalars().first()

            if not note:
                exception = HTTPException(description=f"Note with ID {note_id} not found for this user")
                exception.code = 404
                raise exception
            

            note.title = request.title
            note.content = request.content
            note.updated_at = datetime.datetime.utcnow()
            note.updated_by = user_id

            session.flush()

            return NotesSchema.from_orm(note)

class DeleteNote:
    def __init__(self) -> None:
        self.session = get_session()
    def execute(self, user_id: int, note_id: int) -> NotesSchema:
        with self.session as session:
            note = session.execute(
                select(Notes).where(
                    (Notes.created_by == user_id).__and__(Notes.note_id == note_id).__and__(Notes.deleted_at == None)
                )
            ).scalars().first()
            if not note:
                exception = HTTPException(description="notes not found")
                exception.code = 404
                raise exception

            note.deleted_at = datetime.datetime.utcnow()
            note.deleted_by = user_id
            return NotesSchema.from_orm(note)
