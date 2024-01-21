from flask import Blueprint, jsonify, request

import logging
from api.base.base_schemas import BaseResponse
from middlewares.authentication import (
    refresh_access_token,
    get_user_id_from_access_token,
)
from werkzeug.exceptions import HTTPException
from flask_pydantic import validate
from .schemas import (
    NotesRequest,
    NotesResponse,
    ReadNotesResponse,
    ReadAllNotesRequest,
    ReadAllNotesResponse,
    UpdateNotesRequest,
    UpdateNotesResponse,
    DeleteNotesResponse
)

from .use_cases import NewNotes, GetOneNote, ReadAllNote, UpdateNote, DeleteNote

router = Blueprint("notes", __name__, url_prefix='/api/v1/notes')
logger = logging.getLogger(__name__)

@router.route("/create", methods=['POST'])
@validate()
def create_note(
    body: NotesRequest,  # Use your new request schema
) -> BaseResponse:
    try:
        token_user_id = get_user_id_from_access_token(request)
        
        # Assuming CreateNote use case takes user_id and note data
        resp_data = NewNotes().execute(user_id=token_user_id, request=body)

        return jsonify(NotesResponse(
            status="success",
            message="success create note",
            data=resp_data.__dict__,
        ).__dict__), 200
    
    except HTTPException as ex:
        return jsonify(NotesResponse(
            status="error",
            message=ex.description,
            data=None
        ).__dict__), ex.code
    
    except Exception as e:
        message = str(e)
        return jsonify(NotesResponse(
            status="error",
            message=message,
            data=None
        ).__dict__), 500
    
# Read 1
@router.route("/<int:note_id>", methods=['GET'])
@validate()
def get_one_note(note_id: int):
    try:
        token_user_id = get_user_id_from_access_token(request)

        # Assuming ReadNote use case takes user_id and note_id
        resp_data = GetOneNote().execute(user_id=token_user_id, note_id=note_id)

        return jsonify(ReadNotesResponse(
            status="success",
            message="success get one note",
            data=resp_data.__dict__,
        ).__dict__), 200
    
    except Exception as e:
        message = str(e)
        return jsonify(NotesResponse(
            status="error",
            message=message,
            data=None
        ).__dict__), 500
    
# Read all
@router.route("/", methods=["GET"])
@validate()
def read_all(query: ReadAllNotesRequest) -> ReadAllNotesResponse:
    try:
        logger.info("Start processing read all notes request")

        token_user_id = get_user_id_from_access_token(request)
        resp_data = ReadAllNote().execute(
            user_id=token_user_id, 
            page_params=query, 
            include_deleted=query.include_deleted,
            filter_user=query.filter_user
        )

        logger.info("Successfully processed read all notes request")

        return jsonify(ReadAllNotesResponse(
            status="success",
            message="Success read notes",
            data={"records": resp_data[0], "meta": resp_data[1].__dict__},
        ).__dict__), 200

    except HTTPException as ex:
        logger.error(f"HTTPException: {ex}")
        return jsonify(ReadAllNotesResponse(
            status="error",
            message=ex.description,
            data=None
        ).__dict__), ex.code

    except Exception as e:
        logger.exception("Unhandled exception during read all notes request")
        message = "Failed to read notes"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return jsonify(ReadAllNotesResponse(
            status="error",
            message=message,
            data=None
        ).__dict__), 500

# Update
@router.route("/update/<int:note_id>", methods=['PUT'])
@validate()
def update_note(
    note_id: int,
    body: UpdateNotesRequest,  # Use your new request schema for updating notes
) -> BaseResponse:
    try:
        token_user_id: int = get_user_id_from_access_token(request)

        resp_data = UpdateNote().execute(user_id=token_user_id, note_id=note_id, request=body)

        return jsonify(UpdateNotesResponse(
            status="success",
            message=f"Success update note id: {note_id}",
            data=resp_data.__dict__,
        ).__dict__), 200
    
    except HTTPException as ex:
        return jsonify(UpdateNotesResponse(
            status="error",
            message=ex.description,
            data=None
        ).__dict__), ex.code
    
    except Exception as e:
        message = str(e)
        return jsonify(UpdateNotesResponse(
            status="error",
            message=message,
            data=None
        ).__dict__), 500
    
# Delete
@router.route("/<note_id>", methods=["DELETE"])
@validate()
def delete(note_id: int):
    try:
        token_user_id = get_user_id_from_access_token(request)
        resp_data = DeleteNote().execute(user_id=token_user_id, note_id=note_id)

        return jsonify(DeleteNotesResponse(
            status = "success",
            message = f"success delete note with id {note_id}",
            data = resp_data.__dict__,
        ).__dict__), 200
        
    except HTTPException as ex:
        return jsonify(DeleteNotesResponse(
            status="error",
            message=ex.description,
            data=None
        ).__dict__), ex.code

    except Exception as e:
        message = "failed to delete note"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return jsonify(DeleteNotesResponse(
            status="error",
            message=message,
            data=None
        ).__dict__), 500