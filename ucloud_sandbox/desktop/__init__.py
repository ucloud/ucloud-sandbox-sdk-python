"""
UCloud Sandbox Desktop - Desktop environment sandbox for AI agents.

The Desktop Sandbox allows you to:
- Control mouse and keyboard
- Take screenshots
- Stream desktop via VNC
- Run graphical applications

Example:
```python
from ucloud_sandbox import Desktop

desktop = Desktop.create()
desktop.screenshot()
desktop.left_click(100, 200)
```
"""

from .main import Sandbox

__all__ = [
    "Sandbox",
]
