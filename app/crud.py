from sqlalchemy.orm import Session
from . import models, schemas


def get_all_menu(db: Session):
    return db.query(models.MenuItem).all()


def get_menu(db: Session, id: int):
    return db.query(models.MenuItem).filter(models.MenuItem.id == id).first()


def create_menu_item(db: Session, item: schemas.MenuItemCreate):
    db_item = models.MenuItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def place_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_orders(db: Session):
    return db.query(models.Order).all()
