import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from sources.cred_example_parser import cred_example_error_handler
import httpx

@pytest.mark.asyncio
async def test_cred_example_error_handler_retries_on_409(monkeypatch):
    class DummySource:
        name = "cred_example_source"
        async def fetch_and_save(self):
            return {"retried": True}

    # Simulate HTTP 409 error
    exc = httpx.HTTPStatusError("Conflict", request=None, response=type('r', (), {'status_code': 409})())
    error_details = "409 Conflict"
    source = DummySource()

    # Patch asyncio.sleep to avoid real delay
    with patch("asyncio.sleep", new=AsyncMock()) as sleep_mock:
        task = cred_example_error_handler(source, exc, error_details)
        # Await the retry task
        result = await task
        assert result == {"retried": True}
        sleep_mock.assert_awaited_with(60)

@pytest.mark.asyncio
async def test_cred_example_error_handler_dead_letter(monkeypatch):
    class DummySource:
        name = "cred_example_source"
        async def fetch_and_save(self):
            return {"retried": True}

    exc = Exception("Some error")
    error_details = "Some error occurred"
    source = DummySource()

    # Patch save_to_dead_letter to check it is called
    with patch("sources.cred_example_parser.save_to_dead_letter", new=AsyncMock()) as dead_letter_mock:
        result = cred_example_error_handler(source, exc, error_details)
        # If not a coroutine, just check result
        if asyncio.iscoroutine(result):
            await result
        dead_letter_mock.assert_called()
        assert result["error"] == error_details
        assert result["source"] == source.name

@pytest.mark.asyncio
async def test_cred_example_error_handler_non_409():
    class DummySource:
        name = "cred_example_source"
        async def fetch_and_save(self):
            return {"retried": True}

    exc = httpx.HTTPStatusError("Internal Server Error", request=None, response=type('r', (), {'status_code': 500})())
    error_details = "500 Internal Server Error"
    source = DummySource()

    result = cred_example_error_handler(source, exc, error_details)
    if asyncio.iscoroutine(result):
        result = await result
    assert result["error"] == error_details
    assert result["source"] == source.name 