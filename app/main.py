from fastapi import FastAPI
from .databases import Base, engine
from .routes import menu, order
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Indian Restauarant App")

app.add_middleware(
    CORSMiddleware,
    allow_origins="*"
)


# create DB tables
Base.metadata.create_all(bind=engine)

app.include_router(menu.router, prefix="/menu", tags=['Menu'])
app.include_router(order.router, prefix="/orders", tags=["Oders"])
