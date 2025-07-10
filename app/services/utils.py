from bson import ObjectId

def to_str_id(doc):
    if isinstance(doc, dict):
        return {k: to_str_id(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [to_str_id(v) for v in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc 