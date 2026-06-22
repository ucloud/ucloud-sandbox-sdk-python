"""
UCloud Sandbox Python SDK

A thin wrapper around the E2B SDK that routes to UCloud's sandbox infrastructure.

Quick start:

```python
from ucloud_sandbox import Sandbox

sandbox = Sandbox.create()
result = sandbox.commands.run("echo 'Hello!'")
sandbox.kill()
```

Async:

```python
from ucloud_sandbox import AsyncSandbox

sandbox = await AsyncSandbox.create()
result = await sandbox.commands.run("echo 'Hello!'")
await sandbox.kill()
```

Environment variables:
- UCLOUD_SANDBOX_API_KEY:  API key
- UCLOUD_SANDBOX_REGION:   region code (e.g. cn-wlcb, us-ca), default cn-wlcb
- UCLOUD_SANDBOX_DOMAIN:   full domain override (takes precedence over REGION)
- UCLOUD_SANDBOX_API_URL:  API URL override (optional)
"""

from . import _env

_env.setup()

from e2b import *  # noqa: F401, F403
from e2b import __all__  # noqa: F401
