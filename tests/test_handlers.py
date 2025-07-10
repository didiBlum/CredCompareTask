import pytest
from sources.openlibrary_science import openlibrary_science_handler
from sources.test_webhook_parser import test_webhook_parser
from app.models.item import Item as AppItem
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
import os
import hmac
import hashlib
import json

def sample_openlibrary_response():
    return {
        "key": "/subjects/science",
        "name": "science",
        "subject_type": "subject",
        "work_count": 92712,
        "works": [
            {
                "key": "/works/OL450063W",
                "title": "Frankenstein or The Modern Prometheus",
                "cover_id": 12356249,
                "cover_edition_key": "OL35649409M"
            }
        ]
    }


def test_openlibrary_science_handler_parses_fields():
    data = sample_openlibrary_response()
    item = openlibrary_science_handler(data)
    assert isinstance(item, AppItem)
    assert item.title == "Frankenstein or The Modern Prometheus"
    assert item.topic_name == "science"
    assert "key: /works/OL450063W" in item.content
    assert "cover_id: 12356249" in item.content
    assert "cover_edition_key: OL35649409M" in item.content
    assert isinstance(item.created_at, datetime)


def test_test_webhook_parser_topic_field():
    data = {
        "title": "Triggered item",
        "content": "Random content 5084",
        "topic": "interviews"
    }
    item = test_webhook_parser(data)
    assert isinstance(item, AppItem)
    assert item.title == "Triggered item"
    assert item.content == "Random content 5084"
    assert item.topic_name == "interviews"
    assert item.source_name == "test"
    assert isinstance(item.created_at, datetime)


def test_webhook_signature_validation():
    client = TestClient(app)
    secret = "testsecret"
    os.environ["WEBHOOK_SECRET"] = secret
    payload = {
        "title": "Test",
        "content": "Test content",
        "topic": "interviews"
    }
    body = json.dumps(payload, separators=(",", ":")).encode()
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    headers = {"X-Hub-Signature-256": f"sha256={signature}"}
    # Valid signature
    resp = client.post("/webhook?source=test", data=body, headers={**headers, "Content-Type": "application/json"})
    assert resp.status_code != 401
    # Invalid signature
    bad_headers = {"X-Hub-Signature-256": "sha256=badsignature"}
    resp = client.post("/webhook?source=test", data=body, headers={**bad_headers, "Content-Type": "application/json"})
    assert resp.status_code == 401 