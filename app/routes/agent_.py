
from langchain.schema.messages import AIMessage
from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from .. import crud, databases
from ..helpers import encode_session_id, decode_session_id, convert_to_llm_message
from ..schemas import ChatRequest, ChatResponse, Message
from ..support_agent import LLMWithTools

router = APIRouter()


@router.get('')
def create_agent(db: Session = Depends(databases.get_db)):
    session_obj = crud.create_session(db=db)
    id_value = getattr(session_obj, "id", None)
    if id_value is None:
        raise HTTPException(
            status_code=400, detail="Session is not created please try again")
    session_id = encode_session_id(int(id_value))
    return JSONResponse(status_code=200, content={'session_id': session_id})


@router.post('', response_model=ChatResponse)
def chat_with_agent(request: ChatRequest, db: Session = Depends(databases.get_db)):
    session_id = decode_session_id(request.session_id)
    msgs = crud.get_messages(db, session_id)
    messages = convert_to_llm_message(msgs)
    user_message = Message(
        session_id=session_id,
        role='user',
        content=request.message
    )
    crud.create_message(db, user_message)
    llm_with_tool = LLMWithTools()
    response = llm_with_tool.invoke(messages=messages, input=request.message)
    ai_message = Message(
        session_id=session_id,
        role="assistant",
        content=response
    )
    crud.create_message(db, ai_message)
    return ChatResponse(response=response)
