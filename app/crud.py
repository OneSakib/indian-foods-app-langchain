from sqlalchemy.orm import Session
from . import models, schemas


def get_all_menu(db: Session):
    return db.query(models.MenuItem).all()


def get_menu(db: Session, id: int = 0, name: str = ""):
    if id and id != 0:
        return db.query(models.MenuItem).filter(models.MenuItem.id == id).first()
    else:
        return db.query(models.MenuItem).filter(models.MenuItem.name == name).first()


def create_menu_item(db: Session, item: schemas.MenuItemCreate):
    db_item = models.MenuItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def place_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_orders(db: Session):
    return db.query(models.Order).all()


def create_session(db: Session):
    session_item = models.Session()
    db.add(session_item)
    db.commit()
    db.refresh(session_item)
    return session_item


def get_messages(db: Session, session_id: int):
    return db.query(models.Message).filter(models.Message.session_id == session_id).all()


def create_message(db: Session, message: schemas.Message):
    message_obj = models.Message(**message.model_dump())
    db.add(message_obj)
    db.commit()
    db.refresh(message_obj)
    return message_obj
