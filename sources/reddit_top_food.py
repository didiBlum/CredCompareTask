from app.models.item import Item
from datetime import datetime, timezone
import logging

def reddit_top_food_handler(data):
    # Reddit API: data['data']['children'][0]['data']
    try:
        post = data["data"]["children"][0]["data"]
        title = post.get("title", "(no title)")
        content = post.get("selftext", "")
        created_at = post.get("created_utc")
        if created_at:
            created_at = datetime.fromtimestamp(float(created_at), tz=timezone.utc)
        else:
            created_at = datetime.now(timezone.utc)
        return Item(
            title=title,
            content=content,
            source_name="reddit_top_food",
            topic_name="food",
            created_at=created_at
        )
    except Exception as e:
        logging.getLogger("reddit_top_food_handler").error(f"Failed to parse reddit response: {e}")
        return Item(
            title="(parse error)",
            content=str(e),
            source_name="reddit_top_food",
            topic_name="food",
            created_at=datetime.now(timezone.utc)
        ) 