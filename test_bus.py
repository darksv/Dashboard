import pytest as pytest
from bus import Bus


@pytest.mark.asyncio
async def test_emit():
    bus = Bus()
    handled = 0

    @bus.on('tick')
    async def test(event, data):
        nonlocal handled
        handled += 1

    await bus.emit('tick')
    await bus.emit('tick')

    assert handled == 2
