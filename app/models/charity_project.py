from sqlalchemy import Column, String, Text

from .foundbase import FoundBase


class CharityProject(FoundBase):
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
