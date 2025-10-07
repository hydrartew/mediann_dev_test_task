import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from kafka_app import publish_application

from schemas import Application, ApplicationCreate

from db.cruds import create_application, get_applications_by_user_name, get_all_applications

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/applications", response_model=Application)
async def create_application_endpoint(application_data: ApplicationCreate):
    try:
        db_application = await create_application(application_data)
        
        application = Application(
            id=db_application.id,
            user_name=db_application.user_name,
            description=db_application.description,
            created_at=db_application.created_at
        )
        
        await publish_application(application)
        
        logger.info(f"Application {application.id} created and published to Kafka")
        return application
        
    except Exception as e:
        logger.error(f"Error creating application: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create application")

@router.get("/applications", response_model=List[Application])
async def get_applications(
    user_name: Optional[str] = Query(None, description="Фильтр по имени пользователя"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Размер страницы")
):
    try:
        offset = (page - 1) * size
        
        if user_name:
            db_applications = await get_applications_by_user_name(
                user_name=user_name,
                limit=size,
                offset=offset
            )
        else:
            db_applications = await get_all_applications(
                limit=size,
                offset=offset
            )
        
        applications = [
            Application(
                id=app.id,
                user_name=app.user_name,
                description=app.description,
                created_at=app.created_at
            )
            for app in db_applications
        ]
        
        logger.info(f"Retrieved {len(applications)} applications")
        return applications
        
    except Exception as e:
        logger.error(f"Error retrieving applications: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve applications")
