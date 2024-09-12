from datetime import datetime

from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser

from app.crud import charityproject_crud
from app.schemas.charity_project import CharityProjectDB
from app.services import (
    spreadsheets_create, set_user_permissions, spreadsheets_update_value
)

router = APIRouter()

@router.post(
    '/',
    response_model=list[dict[str, str]],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        # wrapper_services: Aiogoogle = Depends(get_service)
):
    """Только для суперюзеров."""
    closed_proj = await charityproject_crud.get_projects_by_completion_rate(
        session
    )
    return closed_proj
