from pydantic import BaseModel


class MenuItemBase(BaseModel):
    name: str
    description: str
    price: float


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemOut(MenuItemBase):
    id: int

    class config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_name: str
    item_id: int
    quantity: int


class OrderCreate(OrderBase):
    pass


class OrderOut(OrderBase):
    id: int
    item: MenuItemOut

    class Config:
        from_attributes = True


class Message(BaseModel):
    session_id: int
    role: str
    content: str


class MessageOut(Message):
    int: int

    class Config:
        orm_model = True


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
