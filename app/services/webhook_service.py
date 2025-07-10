from app.services.shared_db import save_item_to_db

async def handle_webhook_data(data: dict, source: str):
    data = dict(data)
    data["stream"] = source
    return await save_item_to_db(data) 