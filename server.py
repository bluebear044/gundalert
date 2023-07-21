from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from mongo import DB

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/delete/{id}")
def read_item(id: str):
    return DB().deleteById(id)

@app.get("/list")
def read_list():
    return DB().select()

if __name__ =="__main__":
    uvicorn.run(app, host="172.30.1.1", port=5000, log_level="info")
