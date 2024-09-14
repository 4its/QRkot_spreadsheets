from copy import deepcopy
from datetime import datetime

from aiogoogle import Aiogoogle
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud import charityproject_crud


FORMAT = '%Y/%m/%d %H:%M:%S'
TOO_MANY_COLUMNS = 'Слишком много колонок: {} из {}.'
TOO_MANY_CELLS = 'Слишком много ячеек: {} из {}.'
GOOGLE_MAX_CELLS = 5_000_000
GOOGLE_COLUMNS_LIMIT = 18_278

SPREADSHEET_BODY_TEMPLATE = dict(
    properties=dict(
        title='Отчет на ...',
        locale='ru_RU'
    ),
    sheets=[dict(properties=dict(
        sheetType='GRID',
        sheetId=0,
        title='Список проектов',
        gridProperties=dict(
            rowCount=None,
            columnCount=None,
        )
    ))]
)

TABLE_VALUES = [
    ['Отчёт от', None],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание проекта']
]


async def prepare_data(session: AsyncSession):
    table_values = deepcopy(TABLE_VALUES)
    table_values[0][1] = datetime.now().strftime(FORMAT)
    table_values.extend(
        list(project.values()) for project
        in await charityproject_crud.get_projects_by_completion_rate(session)
    )
    rows = len(table_values)
    columns = max(len(row) for row in table_values)
    return table_values, rows, columns


async def spreadsheets_create(
        wrapper_service: Aiogoogle,
        rows: int,
        columns: int,
        spreadsheet_template: dict = SPREADSHEET_BODY_TEMPLATE,
):
    service = await wrapper_service.discover('sheets', 'v4')
    if columns > GOOGLE_COLUMNS_LIMIT:
        raise ValueError(
            TOO_MANY_COLUMNS.format(columns, GOOGLE_COLUMNS_LIMIT)
        )
    if rows * columns > GOOGLE_MAX_CELLS:
        raise ValueError(
            TOO_MANY_CELLS.format(columns * rows, GOOGLE_MAX_CELLS)
        )
    now_date_time = datetime.now().strftime(FORMAT)
    body = deepcopy(spreadsheet_template)
    body['properties']['title'] = f'Отчет на {now_date_time}'
    body['sheets'][0]['properties']['gridProperties']['rowCount'] = rows
    body['sheets'][0]['properties']['gridProperties']['columnCount'] = columns
    response = await wrapper_service.as_service_account(
        service.spreadsheets.create(json=body)
    )
    return response['spreadsheetId'], response['spreadsheetUrl']


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = dict(
        type='user',
        role='writer',
        emailAddress=settings.email,
    )
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields='id'
        )
    )


async def spreadsheets_update_value(
        wrapper_services: Aiogoogle,
        spreadsheet_id: str,
        table_values: list,
        rows: int,
        columns: int,
) -> None:
    service = await wrapper_services.discover('sheets', 'v4')
    update_body = dict(
        majorDimension='ROWS',
        values=table_values
    )
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{rows}C{columns}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
