import random
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .. import databases, schemas, crud

router = APIRouter()


@router.get('/', response_model=list[schemas.MenuItemOut])
def list_menu(db: Session = Depends(databases.get_db)):
    return crud.get_all_menu(db)


@router.post('/', response_model=schemas.MenuItemOut)
def add_item(item: schemas.MenuItemCreate, db: Session = Depends(databases.get_db)):
    return crud.create_menu_item(db, item)


@router.post('/import')
def import_data(file: UploadFile = File(...), db: Session = Depends(databases.get_db)):
    try:
        df = pd.read_csv(file.file)
        for _, row in df.iterrows():
            item: schemas.MenuItemCreate = schemas.MenuItemCreate(
                name=row['name'], description=row['ingredients'], price=random.randint(50, 500))
            crud.create_menu_item(db, item)
        return JSONResponse(status_code=200, content={"Res": "File Upploaded!", "rows": len(df)})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
