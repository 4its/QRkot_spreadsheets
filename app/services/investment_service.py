from datetime import datetime

from app.models import FoundBase


def spread_donations(
        target: FoundBase,
        sources: list[FoundBase]
) -> list[FoundBase]:
    modified_objects = []
    for source in sources:
        availible_investment = min(
            target.full_amount - target.invested_amount,
            source.full_amount - source.invested_amount
        )
        for item in (target, source):
            item.invested_amount += availible_investment
            if item.invested_amount == item.full_amount:
                item.fully_invested = True
                item.close_date = datetime.now()
        modified_objects.append(source)
    return modified_objects
