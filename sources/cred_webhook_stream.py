from app.models.item import Item
from datetime import datetime, timezone
import logging
logger = logging.getLogger("cred_webhook_stream")

async def cred_webhook_stream(request):
    data = await request.json()
    topic_name = data.get('topic', 'unknown')
    return Item(
        title=data.get('title', 'unknown'),
        content=data.get('content', 'unknown'),
        source_name='cred_webhook_stream',
        topic_name=topic_name,
        created_at=datetime.now(timezone.utc)
    ) 