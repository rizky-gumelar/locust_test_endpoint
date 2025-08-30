from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI()

# Simulasi database
fake_db = {}

# Schema data
class Item(BaseModel):
    name: str
    description: str = None

# @app.get("/items/{item_id}")
# async def get_item(item_id: int):
#     await asyncio.sleep(1)  # Simulasi delay
#     if item_id not in fake_db:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return {"item_id": item_id, "data": fake_db[item_id]}

# @app.post("/items/")
# async def create_item(item_id: int, item: Item):
#     await asyncio.sleep(1)  # Simulasi delay
#     if item_id in fake_db:
#         raise HTTPException(status_code=400, detail="Item already exists")
#     fake_db[item_id] = item
#     return {"message": "Item created", "item_id": item_id, "data": item}

@app.get("/ping")
async def ping():
    await asyncio.sleep(0.2)  # Simulasi proses async (200ms)
    return {"message": "pong"}