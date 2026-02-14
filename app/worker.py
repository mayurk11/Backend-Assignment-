import time
import random
import requests
from io import BytesIO
from PIL import Image as PILImage

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models


def process_job(job_id: int):
    db: Session = SessionLocal()

    try:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()

        if not job:
            return

        if job.status != "ONGOING":
            return

        visits = db.query(models.Visit).filter(
            models.Visit.job_id == job_id
        ).all()

        for visit in visits:

            store = db.query(models.Store).filter(
                models.Store.store_id == visit.store_id
            ).first()

            if not store:
                job.status = "FAILED"
                job.error = visit.store_id
                db.commit()
                return

            images = db.query(models.Image).filter(
                models.Image.visit_id == visit.id
            ).all()

            for image_record in images:
                try:
                    response = requests.get(image_record.image_url)
                    img = PILImage.open(BytesIO(response.content))

                    height = img.height
                    width = img.width
                    perimeter = 2 * (height + width)

                    time.sleep(random.uniform(0.1, 0.4))

                    image_record.height = height
                    image_record.width = width
                    image_record.perimeter = perimeter

                    db.commit()

                except Exception:
                    job.status = "FAILED"
                    job.error = visit.store_id
                    db.commit()
                    return

        
        if job.status == "ONGOING":
            job.status = "COMPLETED"
            db.commit()

    finally:
        db.close()

