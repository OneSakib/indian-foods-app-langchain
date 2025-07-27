
SESSION_ID_CODE = 786786786


def encode_session_id(id: int) -> str:
    return str(SESSION_ID_CODE*id)


def decode_session_id(id: int) -> int:
    return int(id/SESSION_ID_CODE)
