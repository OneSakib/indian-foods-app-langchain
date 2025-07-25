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
        orm_mode = True


class OrderBase(BaseModel):
    customer_name: str
    item_id: int
    quantity: int


class OrderCreate(OrderBase):
    pass


class OrderOut(OrderBase):
    id: int

    class Config:
        orm_mode = True
