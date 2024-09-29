from fastapi import FastAPI, Query
from enum import Enum
from typing import Union, Annotated
from pydantic import BaseModel

app = FastAPI()


class item(BaseModel):
    name: str 
    description: Union[str, None] = None
    price: float 
    tax: Union[float, None] = None
# 由上至下檢查
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.put("/items/{item_id}")
async def update_item(item_id: int, Item:item, q: Union[str, None] = None):
    result = {"item_id": item_id, **Item.model_dump()}
    if q:
        result.update({"q": q})
    return result