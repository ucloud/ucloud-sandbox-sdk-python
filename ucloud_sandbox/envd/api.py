import httpx
import json

from ucloud_sandbox.exceptions import (
    SandboxException,
    NotFoundException,
    AuthenticationException,
    InvalidArgumentException,
    NotEnoughSpaceException,
    format_sandbox_timeout_exception,
)


ENVD_API_FILES_ROUTE = "/files"
ENVD_API_HEALTH_ROUTE = "/health"


def get_message(e: httpx.Response) -> str:
    try:
        message = e.json().get("message", e.text)
    except json.JSONDecodeError:
        message = e.text

    return message


def handle_envd_api_exception(res: httpx.Response):
    if res.is_success:
        return

    res.read()
    trace_id = res.headers.get("X-Trace-ID") or res.headers.get("x-trace-id")

    return format_envd_api_exception(res.status_code, get_message(res), trace_id)


async def ahandle_envd_api_exception(res: httpx.Response):
    if res.is_success:
        return

    await res.aread()
    trace_id = res.headers.get("X-Trace-ID") or res.headers.get("x-trace-id")

    return format_envd_api_exception(res.status_code, get_message(res), trace_id)


def format_envd_api_exception(status_code: int, message: str, trace_id: str = None):
    if status_code == 400:
        return InvalidArgumentException(message, trace_id=trace_id)
    elif status_code == 401:
        return AuthenticationException(message, trace_id=trace_id)
    elif status_code == 404:
        return NotFoundException(message, trace_id=trace_id)
    elif status_code == 429:
        return SandboxException(f"{message}: The requests are being rate limited.", trace_id=trace_id)
    elif status_code == 502:
        return format_sandbox_timeout_exception(message, trace_id)
    elif status_code == 507:
        return NotEnoughSpaceException(message, trace_id=trace_id)
    else:
        return SandboxException(f"{status_code}: {message}", trace_id=trace_id)
