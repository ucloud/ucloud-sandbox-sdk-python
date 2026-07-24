# UCloud Sandbox Python SDK

UCloud Sandbox Python SDK 提供云端沙箱环境，用于安全运行 AI 生成的代码。

## 安装

```bash
pip install ucloud_sandbox
```

## 快速开始

### 1. 获取 API Key

1. 访问 [星图平台](https://astraflow.ucloud.cn/) 注册账号
2. 在 [密钥管理](https://astraflow.ucloud.cn/modelverse/api-keys) 获取 API Key
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

## 私有化 HTTP 部署

私有化服务未配置 TLS 时，设置 sandbox 域名并启用非安全 HTTP：

```bash
export UCLOUD_SANDBOX_DOMAIN=sandbox.example.com
export UCLOUD_SANDBOX_INSECURE_HTTP=true
```

默认管理 API 地址为 `http://api.<domain>`；如果实际地址不符合这个规则，再通过
`UCLOUD_SANDBOX_API_URL` 指定完整 URL。

也可以在调用时传入参数：

```python
from ucloud_sandbox import Sandbox

sandbox = Sandbox.create(
    api_url="http://api.sandbox.example.com",
    domain="sandbox.example.com",
    insecure_http=True,
)
```

`UCLOUD_SANDBOX_INSECURE_HTTP` 默认为 `false`；仅应在可信私有网络中启用。

## 文档
访问 [UCloud Agent Sandbox 文档](https://astraflow.ucloud.cn/docs/agent-sandbox) 获取更多信息。

## 致谢

本项目基于 [E2B](https://github.com/e2b-dev/e2b) 开源项目开发，感谢 E2B 团队的贡献。

## 许可证

MIT License - 详见 [LICENSE](./LICENSE) 文件
