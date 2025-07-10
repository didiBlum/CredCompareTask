from app.models.item import Item
from datetime import datetime, timezone
import ast
import logging
logger = logging.getLogger("cred_example_parser")

def cred_example_parser(data):
    # Try to parse the 'title' field as a stringified dict, fallback to top-level data
    parsed = None
    if isinstance(data.get('title'), str):
        try:
            parsed = ast.literal_eval(data['title'])
            logger.debug(f"Parsed stringified title: {parsed}")
        except Exception as e:
            logger.warning(f"Failed to parse stringified title: {e}")
            parsed = None
    if not parsed or not isinstance(parsed, dict):
        parsed = data
    # Compose the item fields
    content = parsed.get('data')
    if content is None:
        # fallback: use the whole string if present
        content = str(parsed)
    topic_name = parsed.get('topic', '')
    extra = {k: v for k, v in parsed.items() if k not in {'data', 'topic', 'created_at', 'stream'}}
    item_dict = {
        'title': content,
        'content': content,
        'source_name': 'cred_example_source',
        'topic_name': topic_name,
        'created_at': datetime.now(timezone.utc),
        **extra
    }
    logger.debug(f"Final item_dict for cred_example_source: {item_dict}")
    return Item(**item_dict) 