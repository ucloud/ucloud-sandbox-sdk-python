"""
UCloud Sandbox Code Interpreter - Stateful code execution in cloud sandbox.

The Code Interpreter allows you to:
- Run Python and other code in a stateful Jupyter-like environment
- Create and manage execution contexts
- Get rich output including text, images, charts, and more

Example:
```python
from ucloud_sandbox import CodeInterpreter

sandbox = CodeInterpreter.create()
execution = sandbox.run_code("print('Hello, World!')")
print(execution.logs.stdout)
```
"""

from .charts import (
    Chart,
    ChartType,
    Chart2D,
    LineChart,
    ScatterChart,
    BarChart,
    PieChart,
    BoxAndWhiskerChart,
    SuperChart,
    ScaleType,
)
from .models import (
    Context,
    Execution,
    ExecutionError,
    Result,
    MIMEType,
    Logs,
    OutputHandler,
    OutputMessage,
)
from .code_interpreter_sync import Sandbox
from .code_interpreter_async import AsyncSandbox

__all__ = [
    # Main classes
    "Sandbox",
    "AsyncSandbox",
    # Models
    "Context",
    "Execution",
    "ExecutionError",
    "Result",
    "MIMEType",
    "Logs",
    "OutputHandler",
    "OutputMessage",
    # Charts
    "Chart",
    "ChartType",
    "Chart2D",
    "LineChart",
    "ScatterChart",
    "BarChart",
    "PieChart",
    "BoxAndWhiskerChart",
    "SuperChart",
    "ScaleType",
]
