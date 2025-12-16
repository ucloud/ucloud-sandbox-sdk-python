# UCloud Sandbox Python SDK

UCloud Sandbox Python SDK 提供云端沙箱环境，用于安全运行 AI 生成的代码。

## 安装

```bash
pip install ucloud_sandbox
```

## 快速开始

### 1. 获取 API Key

1. 访问 [UCloud Sandbox](https://sandbox.ucloudai.com) 注册账号
2. 在控制台获取 API Key
3. 设置环境变量：

```bash
export UCLOUD_SANDBOX_API_KEY=your_api_key
```

### 2. 基础沙箱

```python
from ucloud_sandbox import Sandbox

with Sandbox.create() as sandbox:
    result = sandbox.commands.run("echo 'Hello, World!'")
    print(result.stdout)
```

### 3. Code Interpreter（代码解释器）

支持有状态的代码执行，变量在多次调用之间保持：

```python
from ucloud_sandbox.code_interpreter import Sandbox

with Sandbox.create() as sandbox:
    sandbox.run_code("x = 1")
    execution = sandbox.run_code("x += 1; print(x)")
    print(execution.logs.stdout)  # ['2']
```

### 4. Desktop（桌面环境）

支持鼠标键盘控制、截图、VNC 流媒体：

```python
from ucloud_sandbox.desktop import Sandbox

desktop = Sandbox.create()

# 截图
screenshot = desktop.screenshot()

# 鼠标操作
desktop.left_click(100, 200)
desktop.write("Hello, World!")

# VNC 流
desktop.stream.start()
print(desktop.stream.get_url())

desktop.kill()
```

## 文档
TODO
访问 [Sandbox 文档](https://docs.sandbox.ucloudai.com) 获取更多信息。

## 致谢

本项目基于 [E2B](https://github.com/e2b-dev/e2b) 开源项目开发，感谢 E2B 团队的贡献。

## 许可证

MIT License - 详见 [LICENSE](./LICENSE) 文件
