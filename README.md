# CredCompareTask

## Deployment

This app is deployed on Heroku.

You can access it here: https://credcompare-task-6c8c449b6667.herokuapp.com/

---

## API Endpoints

### 1. User Management

#### Add a User
```bash
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user123@example.com",
    "name": "Adi"
  }'
```

#### Subscribe to a Topic
Subscribe a user to a topic by user id.
```bash
curl -X POST "http://127.0.0.1:8000/users/USER_ID/topics" \
  -H "Content-Type: application/json" \
  -d '{"topic_name": "TOPIC_NAME_HERE"}'
```
Replace USER_ID with the actual user id.

#### Get Items for a User's Subscribed Topics
Returns up to 20 items from the topics the user is subscribed to, ordered by most recent (or grouped by source by default).
```bash
curl "http://127.0.0.1:8000/users/USER_ID/items?by_source=true&order_by=created_at"
```
- `by_source`: Group items by source (default: true)
- `order_by`: `created_at` (default) or `topic_first_seen`
- `limit`: Max number of items per source (default: 20)

#### Get User Details by User ID
Fetch a user's details by their user id.
```bash
curl "http://127.0.0.1:8000/users/USER_ID"
```
Replace USER_ID with the actual user id.

---

### 2. Items & Topics

#### Add an Item
> If the topic with the given `topic_name` does not exist, it will be automatically created with that name.
```bash
curl -X POST "http://127.0.0.1:8000/items" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sample Item",
    "content": "This is a sample item content.",
    "topic_name": "TOPIC_NAME_HERE",
    "created_at": "2024-06-07T12:00:00"
  }'
```

#### List All Topics
Fetch all topic names in the system.
```bash
curl "http://127.0.0.1:8000/topics"
```
Response example:
```
{
  "topics": ["movies", "news", "finance", ...]
}
```

#### List Topics
```bash
curl "http://127.0.0.1:8000/topics"
```

#### Fetch Items (with Filters and Pagination)
Fetch items with filters for topic name, source name, date range, and pagination. All parameters are optional and can be combined.
```bash
curl "http://127.0.0.1:8000/items?topic_name=movies&source_name=cred_example_source&start_date=2025-07-10T00:00:00&end_date=2025-07-11T00:00:00&skip=0&limit=10&by_source=true"
```
- `topic_name`: Filter by the topic of the item
- `source_name`: Filter by the source of the item
- `start_date`/`end_date`: Filter by item creation time (ISO format)
- `skip`: Number of records to skip (for pagination)
- `limit`: Max number of records to return (default: 20)
- `by_source`: Group items by source (default: true)

#### Fetch Items by Topic Name Only
```bash
curl "http://127.0.0.1:8000/items?topic_name=movies"
```

---

## Webhook Ingestion

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
- The correct handler will be used based on the source name.
- You can add custom webhook authentication and error handling per source.

---

## Periodic Fetching from External Sources

The system can fetch and ingest data from external sources on a schedule, with per-source configuration for:
- **URL**
- **Handler** (for parsing/transforming data)
- **Auth** (Bearer, Basic, API key, custom headers)
- **Cadence** (fetch interval, in seconds)
- **Enabled** (on/off)
- **Max items per fetch**

### Example `sources_config.json` entry:
```json
{
  "sources": [
    {
      "name": "cred_example_source",
      "url": "https://example.com/cred_example_source",
      "handler": "cred_example_handler",
      "auth": { "type": "bearer", "token": "YOUR_TOKEN" },
      "cadence_seconds": 300,
      "enabled": true,
      "max_items": 20,
      "headers": { "X-Custom-Header": "value" },
      "error_handler": "sample_error_handler"
    }
  ]
}
```
- Each source is fetched in its own background task at its own cadence.
- Custom error handling and authentication are supported per source.

## Custom Error Handling for Sources

You can provide custom error handling logic for each source in `sources_config.json` by specifying an `error_handler` field. This allows you to handle specific HTTP errors, implement retry logic, or log errors to a dead letter collection.

### Example: Retry on 409 for cred_example_source

For example, the `cred_example_source` uses a custom error handler that:
- Waits 1 minute and retries if a 409 Conflict error is received
- Logs all errors to the dead letter collection
- Returns a consistent error response for other errors

```json
{
  "name": "cred_example_source",
  "url": "https://credcompare-hr-test-d81ffdfbad0d.herokuapp.com/golf/",
  "cadence_seconds": 300,
  "error_handler": "cred_example_error_handler"
}
```

The handler is implemented in `sources/cred_example_parser.py` and registered in `sources/__init__.py`.

You can implement your own error handler for any source by following this pattern.

---

## Observability

### Health Check
Check if the service is up and running.
```bash
curl http://127.0.0.1:8000/healthz
```
Response: `{ "status": "ok" }`

### Metrics
Get counts of successful and failed fetch and webhook events.
```bash
curl http://127.0.0.1:8000/metrics
```
Response example:
```
{
  "fetch": {"success": 42, "fail": 3},
  "webhook": {"success": 17, "fail": 2}
}
```

### Dead Letter Events
Fetch the last 20 dead letter (failed ingestion) events.
```bash
curl http://127.0.0.1:8000/dead_letter
```
Response example:
```
{
  "dead_letter": [
    {"source_name": "cred_example_source", "error": "...", "exception": "...", "time": "..."},
    ...
  ]
}
```

---

## Tests

This project uses `pytest` for testing. Tests cover user flows, item ingestion, custom error handling, and handler logic.

### Running All Tests

```bash
pytest
```

### Running Specific Test Files

Run only error handling tests:
```bash
pytest tests/test_errors.py
```

Run only handler tests:
```bash
pytest tests/test_handlers.py
```

### What is Tested?
- User and subscription flows
- Item ingestion and queries
- Custom error handling (e.g., 409 retry, dead letter logging)
- Handler logic (e.g., OpenLibrary response parsing)

You can add more tests in the `tests/` directory as needed.
