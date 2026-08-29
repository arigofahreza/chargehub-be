from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/job-titles", tags=["job-titles"])

JOB_TITLES = [
    "Driver",
    "Fleet Manager",
    "Fleet Supervisor",
    "EV Technician",
    "Maintenance Technician",
    "Operations Coordinator",
    "Logistics Coordinator",
]


@router.get("")
def list_job_titles(_: User = Depends(get_current_user)):
    return JOB_TITLES
