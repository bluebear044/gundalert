from typing import Union
from fastapi import FastAPI
import uvicorn
from db import DB

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/delete/{id}")
def read_item(id: int):
    return DB().deleteById(id)

if __name__ =="__main__":
    uvicorn.run(app, host="172.30.1.1", port=5000, log_level="info")
