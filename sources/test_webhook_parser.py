from app.models.item import Item
from datetime import datetime, timezone

async def test_webhook_parser(request):
    # Simple static secret check
    secret = "testsecret"
    received = request.headers.get("X-Test-Webhook-Secret")
    if received != secret:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid or missing webhook secret")
    data = await request.json()
    topic_name = data.get('topic', 'unknown')
    return Item(
        title=data.get('title', 'unknown'),
        content=data.get('content', 'unknown'),
        source_name='test',
        topic_name=topic_name,
        created_at=datetime.now(timezone.utc)
    ) 