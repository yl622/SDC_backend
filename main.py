from fastapi import FastAPI, Path, Query, HTTPException, Cookie, File, UploadFile, Form
from fastapi.responses import JSONResponse
from enum import Enum
from typing import Union, Annotated, List, Optional
from pydantic import BaseModel
from datetime import datetime, time, timedelta
from uuid import UUID

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class Offer(BaseModel):
    name: str
    discount: float
    items: List[Item]

class User(BaseModel):
    username: str
    email: str
    full_name: str

class ExtraDataTypes(BaseModel):
    start_time: datetime
    end_time: time
    repeat_every: timedelta
    process_id: UUID
# from up to down
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def get_item(
    item_id: int,
    q: str | None = Query(None, description="Filter query."),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sorting order: asc or desc.")
):
    if item_id < 1 or item_id > 1000:
        raise HTTPException(status_code=400, detail="Item ID must be between 1 and 1000.")
    if q and (len(q) < 3 or len(q) > 50):
        raise HTTPException(status_code=400, detail="Query 'q' must be between 3 and 50 characters.")
    if q:
        return {
            "item_id": item_id,
            "description": f"This is a sample item that matches the query {q}.",
            "sort_order": sort_order,
        }
    return {
        "item_id": item_id,
        "description": "This is a sample item.",
        "sort_order": sort_order,
    }

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: Union[str, None] = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        if len(q) < 3 or len(q) > 50:
            raise HTTPException(status_code=400, detail="Query 'q' must be between 3 and 50 characters.")
        result.update({"q": q})
    return result

@app.post("/items/filter/")
def filter_items(
    price_min: float = Query(0, description="Minimum price"),
    price_max: float = Query(10000, description="Maximum price"),
    tax_included: bool = Query(True, description="Include tax"),
    tags: List[str] = Query([], description="Tags to filter")
):
    filtered_items = {
        "price_min": price_min,
        "price_max": price_max,
        "tax_included": tax_included,
        "tags": tags,
        "message": "Filter items based on given criteria."
        }
    return filtered_items

@app.post("/items/create_with_fields/")
def create_item_with_fields(item: Item, importance: int):
    return {"item": item, "importance": importance}

@app.post("/offers/")
def create_offer(offer: Offer):
    return {"offer": offer}

@app.post("/users/")
def create_user(user: User):
    return {"user": user}

@app.post("/items/extra_data_types/")
def create_item_with_extra_data(extra_data: ExtraDataTypes):
    return {"extra_data": extra_data, "message": "Extra data processed successfully."}

@app.get("/items/cookies/")
def read_items_from_cookies(session_id: Optional[str] = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(status_code=400, detail="Session ID missing")
    return {"session_id": session_id, "message": "Session retrieved successfully."}
@app.post("/items/form_and_file/")
def create_item_with_form_and_file(
    name: str = Form(..., description="The name of the item"),
    description: Optional[str] = Form(None, description="A description of the item"),
    price: float = Form(..., description="The price of the item"),
    tax: Union[float, None] = Form(None, description="Applicable tax for the item"),
    file: UploadFile = File(..., description="The file associated with the item")
):
    if price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")
    return {
        "message": "Item successfully added",
        "item": {
            "name": name,
            "description": description,
            "price": price,
            "tax": tax
        },
        "file": {
            "filename": file.filename,
            "content_type": file.content_type
        }
    }
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
