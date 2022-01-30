import os
from fastapi import FastAPI, File, UploadFile
import aiofiles
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dborm import Upload, Base
from fastapi.middleware.cors import CORSMiddleware

# IMPORTANT: use this command to run uvicorn:
# python -m uvicorn UIBackend:app --reload
# For some reason directly using uvicorn doesn't detect packages
# database connection setup
engine = create_engine('sqlite:///srflow.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# fastapi initial setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/upload/lr")
async def uploadLR(file: UploadFile):
    # create a row initially devoid of path
    new_upload = Upload()
    id = new_upload.id
    out_file_path=os.path.join(os.getcwd(), 'static','uploads','lr', str(id))
    new_upload.url = '/uploads/lr/'+str(id)
    session.add(new_upload)
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write
    session.commit()
    return {"id": id, "url": new_upload.url}

@app.post("/upload/gt")
async def uploadGT():
    return {"status": "success"}