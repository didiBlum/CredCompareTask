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
    "email": "user123@example.com",
    "name": "Adi"
  }'
```

### Get Items for a User's Subscribed Topics
Returns up to 20 items from the topics the user is subscribed to, ordered by most recent.

```bash
curl "http://127.0.0.1:8000/users/USER_ID/items"
```
Replace USER_ID with the actual user id.

### Webhook: Add Item from External Source
To add an item via webhook, POST to `/webhook` with the `source` as a query parameter. The request body should be a JSON object representing the item data.

```bash
curl -X POST "http://127.0.0.1:8000/webhook?source=sourceA" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Webhook Item Example",
    "content": "This item was sent via webhook.",
    "topic_name": "Technology"
  }'
```

### Fetch Log Events (with Filters and Pagination)
You can fetch log events with filters for date, source, type, and error presence. All parameters are optional.

```bash
curl "http://127.0.0.1:8000/logs?skip=0&limit=10&start_date=2024-06-01T00:00:00&end_date=2024-06-10T23:59:59&source_name=sourceA&type=fetch&include_error=false"
```

- `skip`: Number of records to skip (for pagination)
- `limit`: Max number of records to return
- `start_date`/`end_date`: Filter by event time (ISO format)
- `source_name`: Filter by source
- `type`: `fetch` or `webhook`
- `include_error`: `true` (only errors), `false` (only non-errors)

### Fetch Items with Filters and Pagination
You can fetch items with filters for topic name, source name, date range, and pagination. All parameters are optional and can be combined.

```bash
curl "http://127.0.0.1:8000/items?topic_name=movies&source_name=cred_example_source&start_date=2025-07-10T00:00:00&end_date=2025-07-11T00:00:00&skip=0&limit=10"
```

- `topic_name`: Filter by the topic of the item
- `source_name`: Filter by the source of the item
- `start_date`/`end_date`: Filter by item creation time (ISO format)
- `skip`: Number of records to skip (for pagination)
- `limit`: Max number of records to return

### Fetch Items by Topic Name Only
You can fetch items for a specific topic using the topic_name filter alone.

```bash
curl "http://127.0.0.1:8000/items?topic_name=movies"
```

- `topic_name`: Filter by the topic of the item