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
    if not content:
        content = str(parsed) if parsed else 'unknown'
        logger.warning(f"Missing 'content' in parsed data for source cred_example_source, using default: {content}")
    topic_name = parsed.get('topic') or parsed.get('topic_name')
    if not topic_name:
        topic_name = 'unknown'
        logger.warning(f"Missing 'topic_name' in parsed data for source cred_example_source, using default: {topic_name}")
    title = parsed.get('title') if isinstance(parsed.get('title'), str) and parsed.get('title') != str(parsed) else content
    if not title:
        title = content
        logger.warning(f"Missing 'title' in parsed data for source cred_example_source, using default: {title}")
    item_dict = {
        'title': title or 'unknown',
        'content': content or 'unknown',
        'source_name': 'cred_example_source',
        'topic_name': topic_name or 'unknown',
        'created_at': datetime.now(timezone.utc),
    }
    # Add any extra fields
    extra = {k: v for k, v in parsed.items() if k not in {'data', 'topic', 'topic_name', 'created_at', 'stream', 'title', 'content'}}
    item_dict.update(extra)
    logger.debug(f"Final item_dict for cred_example_source: {item_dict}")
    return Item(**item_dict) 