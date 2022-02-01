import os
from fastapi import FastAPI, File, UploadFile
import aiofiles
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Measure import Measure
from dborm import Upload, Base, LastUpload
from fastapi.middleware.cors import CORSMiddleware
from main import superResolveWithoutGT, superResolve
from sqlalchemy.sql import func
# configuration path
from utils.main_utils import load_model

conf_path = 'confs/SRFlow_CelebA_8X.yml'

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
measure = Measure(use_gpu=False)


@app.get("/")
async def root():
    return {"message": "Hello World"}


async def uploadGeneral(file: UploadFile, type:str):
    # generic function that works for both gt and lr
    # arg: type: either 'gt' or 'lr'
    # get file extension
    ext = file.filename.split('.')[-1]

    # compute id
    num_uploads = session.query(Upload).count()
    id = num_uploads  # the id of the new upload will be the length of num_uploads

    # create the upload object and add it into the table
    new_upload = Upload(file_name=file.filename)
    out_file_path = os.path.join(os.getcwd(), 'static', 'uploads', type, str(id) + '.' + ext)
    new_upload.url = '/static/uploads/'+type+'/' + str(id) + '.' + ext

    # get last upload object
    last_upload = session.query(LastUpload).first()
    if last_upload is None:
        # means this is the first upload
        if type == 'gt':
            last_upload = LastUpload(last_gt_id=id)
        else:
            last_upload = LastUpload(last_lr_id=id)
        session.add(last_upload)
    else:
        if type == 'gt':
            #last_upload.last_gt_id = id
            # since there will only ever be one lastupload object this will work
            session.query(LastUpload).update({LastUpload.last_gt_id:id})
        else:
            #last_upload.last_lr_id = id
            session.query(LastUpload).update({LastUpload.last_lr_id: id})
    session.add(new_upload)

    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write
    session.commit()

    return {"id": id, "url": new_upload.url}

@app.post("/upload/lr")
async def uploadLR(file: UploadFile):
    return await uploadGeneral(file,'lr')

@app.post("/upload/gt")
async def uploadGT(file: UploadFile):
    return await uploadGeneral(file,'gt')

# get multiple sr samples at the same temperature
@app.get('/sr')
async def getSR(withGT:bool = False, numSamples:int=1, heat:float=0.7):
    model, opt = load_model(conf_path)
    conf = conf_path.split('/')[-1].replace('.yml', '')
    lr_dir = opt['dataroot_LR']
    gt_dir = opt['dataroot_GT']
    sr_dir = opt['dataroot_SR']  # the output directory

    sr_urls = []
    for i in range(numSamples):
        if not withGT:
            lr_path, _, sr_path,sr_url = getPaths(num=i)
            superResolveWithoutGT(model,opt,conf,lr_path,sr_path,heat)
            sr_urls.append(sr_url)
        else:
            lr_path, gt_path, sr_path, sr_url = getPaths(num=i)
            superResolve(model, opt, conf, lr_path,gt_path,sr_path,heat,measure)
            sr_urls.append(sr_url)
    return {"urls" : sr_urls}


@app.get('/sr/heatChange')
async def getSR(withGT: bool = False, numSamples: int = 1, heat: float = 0.7):
    if not withGT:
        # todo implement withGT part here
        return
    return {"success": "true"}


def getPaths(num):
    this_dir = os.path.dirname(os.path.realpath(__file__))

    # get the lr, gt and sr paths of the last uploaded image

    # get last uploaded lr and gt upload objects
    last_lr = session.query(Upload,LastUpload).filter(LastUpload.last_lr_id == Upload.id).first()
    last_gt = session.query(Upload, LastUpload).filter(LastUpload.last_gt_id == Upload.id).first()

    # get the paths
    last_lr_path = this_dir+last_lr.Upload.url
    last_gt_path = this_dir+last_gt.Upload.url
    # get file name
    fname = last_lr.Upload.url.split('/')[-1]
    sr_path = this_dir + '/static' + '/sr/'
    sr_path += str(num) +'-'+fname
    sr_url = '/static/sr/'+str(num)+ '-'+fname
    return last_lr_path, last_gt_path, sr_path, sr_url
