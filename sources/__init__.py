from .cred_example_parser import cred_example_parser
from .cred_webhook_stream import cred_webhook_stream
import logging
import asyncio
from app.services.shared_db import save_to_dead_letter

SOURCE_HANDLERS = {
    'cred_example_source': cred_example_parser,
    'cred_webhook_stream': cred_webhook_stream,
}

def get_handler_by_name(name):
    return SOURCE_HANDLERS.get(name)

# Error handler registry

def sample_error_handler(source, exc, error_details):
    logger = logging.getLogger("sample_error_handler")
    logger.error(f"[Sample Handler] Source: {source.name}, Exception: {exc}, Details: {error_details}")
    # Save to dead letter collection
    doc = {
        "source_name": source.name,
        "error": str(error_details),
        "exception": str(exc),
        "time": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
    }
    # If running in an async context, await; otherwise, schedule
    try:
        loop = asyncio.get_running_loop()
        coro = save_to_dead_letter(doc)
        if loop.is_running():
            asyncio.create_task(coro)
        else:
            loop.run_until_complete(coro)
    except RuntimeError:
        # No running loop, fallback
        asyncio.run(save_to_dead_letter(doc))
    return {"source": source.name, "error": f"Handled by sample_error_handler: {error_details}"}

ERROR_HANDLERS = {
    'sample_error_handler': sample_error_handler,
}

def get_error_handler_by_name(name):
    return ERROR_HANDLERS.get(name) 