from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from .. import crud, databases
from ..helpers import encode_session_id, decode_session_id


router = APIRouter()


@router.get('')
def create_chat(db: Session = Depends(databases.get_db)):
    session_obj = crud.create_session(db=db)
    id_value = getattr(session_obj, "id", None)
    if id_value is None:
        raise HTTPException(
            status_code=400, detail="Session is not created please try again")
    session_id = encode_session_id(int(id_value))
    return JSONResponse(status_code=200, content={'session_id': session_id})


# @router.post('',respose)
