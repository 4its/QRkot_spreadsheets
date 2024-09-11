from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charityproject_crud
# from app.crud.donation import donation_crud
from app.models import CharityProject


async def check_name_duplicate(project_name: str, session: AsyncSession):
    """Проверка на повторяющиеся имена для проектов."""
    charity_project_id = await charityproject_crud.get_project_id_by_name(
        project_name, session
    )
    if charity_project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Имя благотворительного проекта должно быть уникальным.'
        )


async def charity_project_exists(
    project_id: int, session: AsyncSession
) -> CharityProject:
    """Проверка, что объект существует. Возвращает объект если существует."""
    charity_project = await charityproject_crud.get(project_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден.'
        )
    return charity_project


async def check_project_is_open(project_id: int, session: AsyncSession):
    """Проверка, что проект еще открыт."""
    charity_project = await charityproject_crud.get(project_id, session)
    if charity_project.close_date and charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нельзя менять закрытый проект.'
        )


async def check_invested_amount(project_id: int, session: AsyncSession):
    """Проверка внесения средств в проект."""
    charity_project = await charityproject_crud.get(project_id, session)
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект внесены средства, его нельзя удалить.'
        )


async def check_invested_summ(
        project_id: int, new_full_amount: int, session: AsyncSession
):
    """Проверка, что новая сумма сборов выше, чем сумма внесенных средств."""
    charity_project = await charityproject_crud.get(project_id, session)
    if charity_project.invested_amount > new_full_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=(
                'Нельзя изменить на сумму, меньшую, чем уже внесено в проект.'
            )
        )
