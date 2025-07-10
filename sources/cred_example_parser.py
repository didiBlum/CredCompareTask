from app.models.item import Item
from datetime import datetime, timezone
import ast
import logging
import asyncio
import httpx
from app.services.shared_db import save_to_dead_letter


logger = logging.getLogger("cred_example_parser")


def cred_example_error_handler(source, exc, error_details):
    logger = logging.getLogger("cred_example_error_handler")
    # Always log to dead letter collection
    doc = {
        "source_name": source.name,
        "error": str(error_details),
        "exception": str(exc),
        "time": datetime.now(timezone.utc).isoformat()
    }
    # Schedule or await dead letter save
    try:
        loop = asyncio.get_running_loop()
        coro = save_to_dead_letter(doc)
        if loop.is_running():
            asyncio.create_task(coro)
        else:
            loop.run_until_complete(coro)
    except RuntimeError:
        asyncio.run(save_to_dead_letter(doc))
    # Check for 409 error
    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 409:
        logger.warning(f"[cred_example_error_handler] 409 Conflict for {source.name}, retrying in 1 minute...")
        async def retry():
            await asyncio.sleep(60)
            try:
                return await source.fetch_and_save()
            except Exception as e:
                logger.error(f"[cred_example_error_handler] Retry failed: {e}")
                return {"source": source.name, "error": f"Retry after 409 failed: {e}"}
        return asyncio.create_task(retry())
    # For all other errors, just log and return error info
    logger.error(f"[cred_example_error_handler] Non-409 error: {error_details}")
    return {"source": source.name, "error": str(error_details), "exception": str(exc)}


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