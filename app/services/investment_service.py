from datetime import datetime

from app.models import FoundBase

def update_investment(
    item: FoundBase,
    available_investment: int,
    current_time: datetime
):
    item.invested_amount += available_investment
    if item.invested_amount == item.full_amount:
        item.fully_invested = True
        item.close_date = current_time


def spread_donations(
    target: FoundBase,
    sources: list[FoundBase]
) -> list[FoundBase]:
    updated = []
    current_time = datetime.now()
    if target.full_amount == target.invested_amount:
        target.fully_invested = True
        target.close_date = current_time
        return updated
    for source in sources:
        available_investment = min(
            target.full_amount - target.invested_amount,
            source.full_amount - source.invested_amount
        )
        for item in (target, source):
            update_investment(item, available_investment, current_time)
        updated.append(source)
        if target.fully_invested:
            break
    return updated
