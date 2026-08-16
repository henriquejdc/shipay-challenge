import pytest

from application.retry import RetryPolicy


@pytest.mark.asyncio
async def test_retry_policy_retries_until_success():
    policy = RetryPolicy(attempts=3, base_delay_seconds=0)
    calls = {"count": 0}

    async def operation():
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("temporary failure")
        return "ok"

    result = await policy.run(operation)

    assert result == "ok"
    assert calls["count"] == 3


@pytest.mark.asyncio
async def test_retry_policy_raises_last_error():
    policy = RetryPolicy(attempts=2, base_delay_seconds=0)

    async def operation():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await policy.run(operation)
