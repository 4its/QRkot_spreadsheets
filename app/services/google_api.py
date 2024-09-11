from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings


FORMAT = "%Y/%m/%d %H:%M:%S"

TABLE_VALUES = [
    ['Отчёт от', None],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание проекта']
]
TABLE_COLUMNS = (max(len(element) for element in TABLE_VALUES))  # TODO: Не факт что пригодится
TABLE_ROWS = len(TABLE_VALUES)  # TODO: Не факт что пригодится


async def spreadsheets_create(
        wrapper_service: Aiogoogle,
        count_rows=100
) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_service.discover('sheets', 'v4')
    spreadsheet_body = dict(
        properties=dict(
            title=f'Отчет на {now_date_time}', locale='ru_RU'
        ),
        sheets=[dict(
            properties=dict(
                sheetType='GRID',
                sheetId=0,
                title='Список проектов',
                gridProperties=dict(
                    rowCount=count_rows,
                    columnCount=TABLE_COLUMNS,
                )
            )
        )],
    )
    response = await wrapper_service.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    # print(f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}')  # TODO: Удалить перед ревью
    return spreadsheet_id

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
        spreadsheet_id: str,
        reservations: list,
        wrapper_services: Aiogoogle
) -> None:
    table_values = TABLE_VALUES.copy()
    table_values[0][1] = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    # table_values = [
    #     ['Отчёт от', now_date_time],
    #     ['Топ проектов по скорости закрытия'],
    #     ['Название проекта', 'Кол-во бронирований']
    # ]
    # Здесь в таблицу добавляются строчки
    for res in reservations:
        new_row = [str(res['meetingroom_id']), str(res['count'])]
        table_values.append(new_row)
    update_body = dict(
        majorDimension='ROWS',
        values=table_values
    )
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
