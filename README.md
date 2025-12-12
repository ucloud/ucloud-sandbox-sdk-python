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

### 2. 运行代码

```python
from ucloud_sandbox import Sandbox

with Sandbox.create() as sandbox:
    sandbox.run_code("x = 1")
    execution = sandbox.run_code("x += 1; x")
    print(execution.text)  # 输出: 2
```

## 文档
TODO
访问 [Sandbox 文档](https://docs.sandbox.ucloudai.com) 获取更多信息。

## 致谢

本项目基于 [E2B](https://github.com/e2b-dev/e2b) 开源项目开发，感谢 E2B 团队的贡献。

## 许可证

MIT License - 详见 [LICENSE](./LICENSE) 文件
