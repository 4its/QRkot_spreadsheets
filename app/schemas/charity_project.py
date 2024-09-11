from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt

FIELD_MIN_LENGTH = 1
FIELD_MAX_LENGTH = 100


class CharityProjectBase(BaseModel):
    name: str = Field(
        ..., min_length=FIELD_MIN_LENGTH, max_length=FIELD_MAX_LENGTH
    )
    description: str = Field(..., min_length=FIELD_MIN_LENGTH)
    full_amount: PositiveInt

    class Config:
        extra = Extra.forbid


class CharityProjectCreate(CharityProjectBase):

    class Config(CharityProjectBase.Config):
        schema_extra = {
            'example': {
                'name': 'Название лучшего благотворительного проекта',
                'description': 'Описание этого волшебного проекта',
                'full_amount': 100000
            }
        }


class CharityProjectUpdate(CharityProjectBase):
    name: Optional[str] = Field(
        None, min_length=FIELD_MIN_LENGTH, max_length=FIELD_MAX_LENGTH,
    )
    description: Optional[str] = Field(None, min_length=FIELD_MIN_LENGTH)
    full_amount: Optional[PositiveInt]

    class Config(CharityProjectBase.Config):
        schema_extra = {
            'example': {
                'name': 'Смена название на еще более милое и привлекательное',
                'description': 'Супер подробное описание замечательного проекта',
                'full_amount': 1_000_000
            }
        }



class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
