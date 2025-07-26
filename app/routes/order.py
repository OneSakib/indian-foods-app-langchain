from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from .. import databases, schemas, crud, models


router = APIRouter()


@router.get('', response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(databases.get_db)):
    return crud.get_orders(db)


@router.post('', response_model=schemas.OrderOut)
def place_order(order: schemas.OrderCreate, db: Session = Depends(databases.get_db)):
    menu_item = crud.get_menu(db, order.item_id)
    if not menu_item:
        raise HTTPException(status_code=400, detail="Menu Item is not Exist!")
    return crud.place_order(db, order)
