from datetime import datetime
from sqlalchemy.orm import Session
from app import models

from fastapi import HTTPException

from sqlalchemy import func



def create_job(db: Session, request_data):

    # Create Job first
    new_job = models.Job(status="ONGOING")
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # Validate all stores BEFORE creating visits
    for visit in request_data.visits:
        store = db.query(models.Store).filter(
            models.Store.store_id == visit.store_id
        ).first()

        if not store:
            new_job.status = "FAILED"
            new_job.error = f"Store {visit.store_id} not found"
            db.commit()
            return new_job.id

    # If all stores valid → create visits & images
    for visit in request_data.visits:
        new_visit = models.Visit(
            job_id=new_job.id,
            store_id=visit.store_id,
            visit_time=visit.visit_time
        )
        db.add(new_visit)
        db.commit()
        db.refresh(new_visit)

        for url in visit.image_url:
            new_image = models.Image(
                visit_id=new_visit.id,
                image_url=url
            )
            db.add(new_image)

        db.commit()

    return new_job.id



def get_job_status(db: Session, job_id: int):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=400, detail="Job ID does not exist")

    response = {
        "status": job.status,
        "job_id": job.id
    }

    if job.status == "FAILED":
        response["error"] = [{"store_id": job.error}]

    return response



def get_visit_report(db: Session, area: str, storeid: str, startdate: datetime, enddate: datetime):

    # Validate store exists
    store = db.query(models.Store).filter(
        models.Store.store_id == storeid,
        models.Store.area_code == area
    ).first()

    if not store:
        raise HTTPException(status_code=400, detail="Invalid area or store_id")

    # Query with aggregation
    results = (
        db.query(
            models.Visit.store_id,
            func.date(models.Visit.visit_time).label("visit_date"),
            func.sum(models.Image.perimeter).label("total_perimeter")
        )
        .join(models.Image, models.Image.visit_id == models.Visit.id)
        .filter(
            models.Visit.store_id == storeid,
            models.Visit.visit_time >= startdate,
            models.Visit.visit_time <= enddate
        )
        .group_by(models.Visit.store_id, func.date(models.Visit.visit_time))
        .all()
    )

    formatted_data = []

    for row in results:
        formatted_data.append({
            "date": row.visit_date,
            "perimeter": row.total_perimeter
        })

    return {
        "results": [
            {
                "store_id": store.store_id,
                "area": store.area_code,
                "store_name": store.store_name,
                "data": formatted_data
            }
        ]
    }
