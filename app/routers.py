from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SubmitJobRequest, SubmitJobResponse
from app.services import create_job
from app import models


from fastapi import BackgroundTasks
from app.worker import process_job

from app.services import get_job_status

from app.services import get_visit_report
from datetime import datetime




router = APIRouter(prefix="/api") 
# router = APIRouter()

@router.get("/")
def server_check():
    return {"message": "Service is running"}


@router.post("/submit/", response_model=SubmitJobResponse)
def submit_job(
    request: SubmitJobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    job_id = create_job(db, request)

    # Fetch job to check status
    job = db.query(models.Job).filter(models.Job.id == job_id).first()

    if job.status == "ONGOING":
        background_tasks.add_task(process_job, job_id)

    return {"job_id": job_id}


@router.get("/status")
def job_status(jobid: int, db: Session = Depends(get_db)):
    return get_job_status(db, jobid)


@router.get("/visits")
def visit_report(
    area: str,
    storeid: str,
    startdate: datetime,
    enddate: datetime,
    db: Session = Depends(get_db)
):
    return get_visit_report(db, area, storeid, startdate, enddate)
