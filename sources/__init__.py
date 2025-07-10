from .cred_example_parser import cred_example_parser

SOURCE_HANDLERS = {
    'cred_example_source': cred_example_parser,
    'cred_example_handler': cred_example_parser,  
}

def get_handler_by_name(name):
    return SOURCE_HANDLERS.get(name)

# Error handler registry

def sample_error_handler(source, exc, error_details):
    import logging
    logger = logging.getLogger("sample_error_handler")
    logger.error(f"[Sample Handler] Source: {source.name}, Exception: {exc}, Details: {error_details}")
    return {"source": source.name, "error": f"Handled by sample_error_handler: {error_details}"}

ERROR_HANDLERS = {
    'sample_error_handler': sample_error_handler,
}

def get_error_handler_by_name(name):
    return ERROR_HANDLERS.get(name) 