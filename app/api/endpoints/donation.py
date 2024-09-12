from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.donation import donation_crud
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationDB, DonationGet
from app.services.investment_service import spread_donations

router = APIRouter()


@router.post('/', response_model=DonationGet,)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
) -> DonationGet:
    """Создание пожертвования."""
    new_donation = await donation_crud.create(donation, session, user)
    return await spread_donations(session, new_donation)


@router.get('/my', response_model=list[DonationGet])
async def get_all_user_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """Получить все пожертвования пользователя."""
    return await donation_crud.get_user_donations(session, user)


@router.get('/', response_model=list[DonationDB],)
async def get_whole_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_superuser),
):
    """Только для супер пользователей. Получение всех(совсем) пожертвований."""
    return await donation_crud.get_multi(session)
