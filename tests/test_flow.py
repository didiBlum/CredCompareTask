import pytest
import httpx
from fastapi import status
import asyncio

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_user_subscription_flow():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # 1. Add user
        user_data = {
            "email": "testuser@example.com",
            "name": "Test User"
        }
        resp = await client.post("/users", json=user_data)
        assert resp.status_code == status.HTTP_201_CREATED
        user_id = resp.json()["user_id"]

        # 2. Subscribe to a topic
        topic_name = "TestTopic"
        resp = await client.post(f"/users/{user_id}/topics", json={"topic_name": topic_name})
        assert resp.status_code == 200

        # 3. Add item to the same topic
        item1 = {
            "title": "Item 1",
            "content": "Content 1",
            "source_name": "sourceA",
            "topic_name": topic_name,
            "created_at": "2024-06-07T12:00:00"
        }
        resp = await client.post("/items", json=item1)
        assert resp.status_code == 200
        item1_id = resp.json()["item"]["_id"]

        # 4. Add item to another topic
        item2 = {
            "title": "Item 2",
            "content": "Content 2",
            "source_name": "sourceB",
            "topic_name": "OtherTopic",
            "created_at": "2024-06-07T13:00:00"
        }
        resp = await client.post("/items", json=item2)
        assert resp.status_code == 200
        item2_id = resp.json()["item"]["_id"]

        # 5. Get items for the user
        resp = await client.get(f"/users/{user_id}/items")
        assert resp.status_code == 200
        # The response is a dict of {source_name: [items]}
        items_by_source = resp.json()
        all_items = []
        for items in items_by_source.values():
            all_items.extend(items)
        assert len(all_items) == 1
        assert all_items[0]["_id"] == item1_id
        assert all_items[0]["title"] == "Item 1" 