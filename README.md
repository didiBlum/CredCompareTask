# CredCompareTask

## Deployment

This app is deployed on Heroku.

You can access it here: https://credcompare-task-6c8c449b6667.herokuapp.com/

## API Usage Examples

### Subscribe to a Topic
```bash
curl -X POST "http://127.0.0.1:8000/subscribe" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID_HERE", "topic_name": "TOPIC_NAME_HERE"}'
```

### Add an Item
> Note: If the topic with the given `topic_name` does not exist, it will be automatically created with that name.

```bash
curl -X POST "http://127.0.0.1:8000/items" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sample Item",
    "content": "This is a sample item content.",
    "source_id": "SOURCE_ID_HERE",
    "topic_name": "TOPIC_NAME_HERE",
    "created_at": "2024-06-07T12:00:00"
  }'
```

### List Topics
```bash
curl "http://127.0.0.1:8000/topics"
```

### Add a User
```bash
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "user123",
    "email": "user123@example.com",
    "name": "Alice Example",
    "subscribed_topics": []
  }'
```