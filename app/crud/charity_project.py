from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectUpdate
)


class CRUDCharityProject(
    CRUDBase[CharityProject, CharityProjectCreate, CharityProjectUpdate]
):

    async def get_project_id_by_name(
            self, charityproject_name: str, session: AsyncSession,
    ) -> Optional[int]:
        charityproject = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == charityproject_name
            )
        )
        return charityproject.scalars().first()


charityproject_crud = CRUDCharityProject(CharityProject)
