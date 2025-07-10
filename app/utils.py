from bson import ObjectId

def convert_object_ids_to_str(doc):
    if isinstance(doc, dict):
        return {k: convert_object_ids_to_str(v) if k != '_id' else (str(v) if isinstance(v, ObjectId) else v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [convert_object_ids_to_str(v) for v in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc 