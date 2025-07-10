from app.models.item import Item
from datetime import datetime, timezone
import logging

def reddit_top_science_handler(data):
    # Reddit API: data['data']['children'][0]['data']
    try:
        post = data["data"]["children"][0]["data"]
        title = post.get("title", "(no title)")
        url = post.get("url", "")
        created_at = post.get("created_utc")
        if created_at:
            created_at = datetime.fromtimestamp(float(created_at), tz=timezone.utc)
        else:
            created_at = datetime.now(timezone.utc)
        return Item(
            title=title,
            content=url,
            source_name="reddit_top_science",
            topic_name="science",
            created_at=created_at
        )
    except Exception as e:
        logging.getLogger("reddit_top_science_handler").error(f"Failed to parse reddit response: {e}")
        return Item(
            title="(parse error)",
            content=str(e),
            source_name="reddit_top_science",
            topic_name="science",
            created_at=datetime.now(timezone.utc)
        ) 