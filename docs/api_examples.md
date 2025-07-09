# API Example Requests

## Example Data

- user_id: "user123"
- topic_name: "Technology"
- topic_name: "Finance"
- Example Item 1:
  - title: "AI Breakthrough"
  - content: "A new AI model surpasses human performance."
  - source_id: "sourceA"
  - topic_name: "Technology"
  - created_at: "2024-06-07T12:00:00"
- Example Item 2:
  - title: "Stock Market Update"
  - content: "Markets rally after positive economic news."
  - source_id: "sourceB"
  - topic_name: "Finance"
  - created_at: "2024-06-07T13:00:00"

## Subscribe to a Topic
```bash
curl -X POST "http://127.0.0.1:8000/subscribe" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "topic_name": "Technology"}'
```

## Add an Item (Technology)
> Note: If the topic with the given `topic_name` does not exist, it will be automatically created with that name.

```bash
curl -X POST "http://127.0.0.1:8000/items" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Breakthrough",
    "content": "A new AI model surpasses human performance.",
    "source_id": "sourceA",
    "topic_name": "Technology",
    "created_at": "2024-06-07T12:00:00"
  }'
```

## Add an Item (Finance)
```bash
curl -X POST "http://127.0.0.1:8000/items" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Stock Market Update",
    "content": "Markets rally after positive economic news.",
    "source_id": "sourceB",
    "topic_name": "Finance",
    "created_at": "2024-06-07T13:00:00"
  }'
```

## List Topics
```bash
curl "http://127.0.0.1:8000/topics"
```

## Add a User
```bash
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user123@example.com",
    "name": "Adi",
    "subscribed_topics": []
  }'
```

## Get Items for a User's Subscribed Topics
Returns up to 20 items from the topics the user is subscribed to, ordered by most recent.

```bash
curl "http://127.0.0.1:8000/users/user123/items"
```
Replace user123 with the actual user id. 