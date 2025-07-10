from app.models.item import Item
from datetime import datetime, timezone
import logging

def openlibrary_science_handler(data):
    try:
        topic = data.get("name", "openlibrary")
        work = data["works"][0]
        title = work.get("title", "(no title)")
        key = work.get("key", "")
        cover_id = work.get("cover_id", "")
        cover_edition_key = work.get("cover_edition_key", "")
        content = f"key: {key}, cover_id: {cover_id}, cover_edition_key: {cover_edition_key}"
        created_at = datetime.now(timezone.utc)
        return Item(
            title=title,
            content=content,
            source_name="openlibrary_science",
            topic_name=topic,
            created_at=created_at
        )
    except Exception as e:
        logging.getLogger("openlibrary_science_handler").error(f"Failed to parse openlibrary response: {e}")
        return Item(
            title="(parse error)",
            content=str(e),
            source_name="openlibrary_science",
            topic_name="openlibrary",
            created_at=datetime.now(timezone.utc)
        ) 