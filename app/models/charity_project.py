from sqlalchemy import Column, String, Text

from .foundbase import FoundBase


class CharityProject(FoundBase):
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    def __repr__(self):
        return(
            f'<CharityProject({self.name=}, '
            f'{self.description=}, '
            f'{super().__repr__()})>'
        )
