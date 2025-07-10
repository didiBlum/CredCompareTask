from app.models.item import Item
from datetime import datetime, timezone
import logging
logger = logging.getLogger("cred_webhook_stream")

def cred_webhook_stream(data):
    # Ensure required fields
    content = data.get('data')
    if not content:
        content = str(data) if data else 'unknown'
        logger.warning(f"Missing 'content' in webhook stream data, using default: {content}")
    topic_name = data.get('topic') or data.get('topic_name')
    if not topic_name:
        topic_name = 'unknown'
        logger.warning(f"Missing 'topic_name' in webhook stream data, using default: {topic_name}")
    title = content
    item_dict = {
        'title': title or 'unknown',
        'content': content or 'unknown',
        'source_name': data.get('stream', 'cred_webhook_stream'),
        'topic_name': topic_name or 'unknown',
        'created_at': data.get('created_at') or datetime.now(timezone.utc),
    }
    # Add any extra fields
    extra = {k: v for k, v in data.items() if k not in {'data', 'topic', 'topic_name', 'created_at', 'stream', 'title', 'content'}}
    item_dict.update(extra)
    logger.debug(f"Final item_dict for cred_webhook_stream: {item_dict}")
    return Item(**item_dict) 