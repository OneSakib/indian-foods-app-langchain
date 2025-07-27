
from typing import List
from .schemas import Message
from langchain.schema.messages import HumanMessage, AIMessage, ToolMessage
SESSION_ID_CODE = 786786786


def encode_session_id(id: int) -> str:
    return str(SESSION_ID_CODE*id)


def decode_session_id(id: str) -> int:
    int_id = int(id)
    return int(int_id/SESSION_ID_CODE)


def convert_to_llm_message(msgs):
    messages = []
    for msg in msgs:
        if msg.role == 'user':
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == 'assistant':
            messages.append(AIMessage(content=msg.content))
        elif msg.role == 'tool':
            messages.append(ToolMessage(
                content=msg.content, tool_call_id=msg.tool_id))
    return messages
