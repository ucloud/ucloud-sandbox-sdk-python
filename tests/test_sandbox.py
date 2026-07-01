"""
Integration tests for ucloud_sandbox.

Requires UCLOUD_SANDBOX_API_KEY to be set before running:
    export UCLOUD_SANDBOX_API_KEY=your_api_key
    pytest tests/test_sandbox.py -v
"""

import pytest

from ucloud_sandbox import AsyncSandbox, Sandbox


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------


def test_create_and_kill():
    sbx = Sandbox.create(timeout=60)
    assert sbx.sandbox_id
    sbx.kill()


def test_run_command():
    with Sandbox.create(timeout=60) as sbx:
        result = sbx.commands.run("echo hello")
        assert result.stdout.strip() == "hello"
        assert result.exit_code == 0


def test_connect():
    sbx = Sandbox.create(timeout=60)
    try:
        connected = Sandbox.connect(sbx.sandbox_id)
        result = connected.commands.run("echo connected")
        assert result.stdout.strip() == "connected"
    finally:
        sbx.kill()


def test_pause_and_resume():
    sbx = Sandbox.create(timeout=60, lifecycle={"on_timeout": "pause"})
    try:
        sbx.commands.run("echo before-pause")
        sbx.pause()
        resumed = Sandbox.connect(sbx.sandbox_id)
        result = resumed.commands.run("echo after-resume")
        assert result.stdout.strip() == "after-resume"
    finally:
        sbx.kill()


# ---------------------------------------------------------------------------
# Async
# ---------------------------------------------------------------------------


async def test_async_create_and_kill():
    sbx = await AsyncSandbox.create(timeout=60)
    assert sbx.sandbox_id
    await sbx.kill()


async def test_async_run_command():
    async with await AsyncSandbox.create(timeout=60) as sbx:
        result = await sbx.commands.run("echo hello")
        assert result.stdout.strip() == "hello"
        assert result.exit_code == 0


async def test_async_connect():
    sbx = await AsyncSandbox.create(timeout=60)
    try:
        connected = await AsyncSandbox.connect(sbx.sandbox_id)
        result = await connected.commands.run("echo connected")
        assert result.stdout.strip() == "connected"
    finally:
        await sbx.kill()


async def test_async_pause_and_resume():
    sbx = await AsyncSandbox.create(timeout=60, lifecycle={"on_timeout": "pause"})
    try:
        await sbx.commands.run("echo before-pause")
        await sbx.pause()
        resumed = await AsyncSandbox.connect(sbx.sandbox_id)
        result = await resumed.commands.run("echo after-resume")
        assert result.stdout.strip() == "after-resume"
    finally:
        await sbx.kill()
