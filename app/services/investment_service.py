from datetime import datetime
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Donation, CharityProject
from app.crud import charityproject_crud, donation_crud


async def close_object(
    session: AsyncSession, obj_item: Union[Donation, CharityProject]
):
    obj_item.fully_invested = 1
    obj_item.close_date = datetime.now()
    session.add(obj_item)


async def refresh_object(
        session: AsyncSession, obj_item
):
    await session.refresh(obj_item)
    return obj_item


async def spread_donations(
    session: AsyncSession, obj_item: Union[Donation, CharityProject]
):
    if obj_item.full_amount == obj_item.invested_amount:
        await close_object(session, obj_item)
        await session.commit()
        await session.refresh(obj_item)
        return obj_item

    projects = await charityproject_crud.get_opened(session)
    donations = await donation_crud.get_opened(session)

    for project in projects:
        for donation in donations:
            project_balance = project.full_amount - project.invested_amount
            donation_balance = donation.full_amount - donation.invested_amount

            if project_balance == donation_balance:
                project.invested_amount = project.full_amount
                donation.invested_amount = donation.full_amount
                await close_object(session, project)
                await close_object(session, donation)

            elif project_balance > donation_balance:
                project.invested_amount += donation_balance
                donation.invested_amount += donation_balance
                await close_object(session, donation)
                await charityproject_crud.add_to_session(session, project)

            elif donation_balance > project_balance:
                project.invested_amount += project_balance
                donation.invested_amount += project_balance
                await close_object(session, project)
                await donation_crud.add_to_session(session, donation)

    if isinstance(obj_item, CharityProject):
        return await charityproject_crud.commit_and_refresh(session, obj_item)
    return await donation_crud.commit_and_refresh(session, obj_item)
