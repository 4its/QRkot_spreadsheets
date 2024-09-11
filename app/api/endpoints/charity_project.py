from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_name_duplicate, charity_project_exists, check_invested_summ,
    check_invested_amount, check_project_is_open
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charityproject_crud
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.services.investment_service import spread_donations

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
        project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    await check_name_duplicate(project.name, session)
    new_charity_project = await charityproject_crud.create(
        project, session
    )
    return await spread_donations(session, new_charity_project)


@router.get('/', response_model=list[CharityProjectDB])
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    """Получение всех объектов."""
    return await charityproject_crud.get_multi(session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперпользователей."""
    charity_project = await charity_project_exists(project_id, session)
    await check_project_is_open(charity_project.id, session)
    if obj_in.name:
        await check_name_duplicate(obj_in.name, session)
    if obj_in.full_amount:
        await check_invested_summ(
            charity_project.id, obj_in.full_amount, session
        )
    charity_project = await charityproject_crud.update(
        charity_project, obj_in, session
    )
    return await spread_donations(session, charity_project)


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперпользователей."""
    charity_project = await charity_project_exists(project_id, session)
    await check_project_is_open(project_id, session)
    await check_invested_amount(project_id, session)
    return await charityproject_crud.remove(
        charity_project, session
    )
