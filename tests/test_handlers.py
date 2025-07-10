import pytest
from sources.openlibrary_science import openlibrary_science_handler
from app.models.item import Item
from datetime import datetime

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
    assert isinstance(item, Item)
    assert item.title == "Frankenstein or The Modern Prometheus"
    assert item.topic_name == "science"
    assert "key: /works/OL450063W" in item.content
    assert "cover_id: 12356249" in item.content
    assert "cover_edition_key: OL35649409M" in item.content
    assert isinstance(item.created_at, datetime) 