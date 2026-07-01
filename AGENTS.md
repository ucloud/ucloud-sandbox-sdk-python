# 项目说明

这个仓库是 UCloud Sandbox 的 Python SDK。UCloud Sandbox 服务的 API 与 E2B 完全兼容，所以这个项目本质上是把 E2B 相关 Python SDK 的上游代码同步到本仓库中，再在同步后的代码基础上修改环境变量名称、错误描述、文案和品牌信息，使其面向 UCloud Sandbox。

需要特别注意：本仓库不只是同步 E2B 主 Python SDK，还会把 E2B 的两个独立 Python SDK 一起合并进来：

- `code-interpreter`
- `desktop`

因此，后续修改时要把 `ucloud_sandbox/` 视为合并后的 SDK 包，而不是单一上游仓库的简单镜像。

# 目录结构

- `ucloud_sandbox/`
  - 本项目主要 SDK 代码目录。
  - 这是发布给用户使用的 Python 包主体。
  - 代码来源于多个 E2B 上游 Python SDK，同步后会继续进行 UCloud 相关改造。

- `upstream/`
  - 上游源码目录。
  - 这里的内容通过 git submodules 管理，通常不要直接在这里做业务修改。
  - 如果需要更新上游，应更新 submodule 后再运行同步脚本。

上游 submodule 与同步目标的关系如下：

- `upstream/e2b`
  - 上游仓库：`https://github.com/e2b-dev/E2B.git`
  - 上游 Python SDK 位置：`upstream/e2b/packages/python-sdk/e2b`
  - 同步到：`ucloud_sandbox/`

- `upstream/code-interpreter`
  - 上游仓库：`https://github.com/e2b-dev/code-interpreter.git`
  - 上游 Python SDK 位置：`upstream/code-interpreter/python/e2b_code_interpreter`
  - 同步到：`ucloud_sandbox/code_interpreter/`
  - 同步后保留本项目原有目录命名 `code_interpreter`。

- `upstream/desktop`
  - 上游仓库：`https://github.com/e2b-dev/desktop.git`
  - 上游 Python SDK 位置：`upstream/desktop/packages/python-sdk/e2b_desktop`
  - 同步到：`ucloud_sandbox/desktop/`
  - 同步后保留本项目原有目录命名 `desktop`。

# 同步脚本

- `scripts/sync_upstreams.sh`
  - 上游代码同步入口。
  - 会检查 `upstream/` 下的 submodules 是否已经初始化；如果没有，会执行 `git submodule update --init --recursive`。
  - 会将 E2B 主 Python SDK 复制到 `ucloud_sandbox/`，将 `e2b_connect` 复制到根目录 `e2b_connect/`，并将 `code-interpreter` 和 `desktop` 的 Python SDK 分别复制到 `ucloud_sandbox/code_interpreter/` 和 `ucloud_sandbox/desktop/`。
  - 这个脚本只同步上游代码，不会自动同步依赖，也不会自动执行 UCloud 定制 hack。
  - 该脚本会覆盖 `ucloud_sandbox/`、`ucloud_sandbox/code_interpreter/` 和 `ucloud_sandbox/desktop/` 中的内容。运行前要确认当前工作区里的 UCloud 改造是否已经保存或确认可以被覆盖。

- `scripts/sync_dependencies.py`
  - 依赖同步脚本。
  - 会读取三个上游 Python SDK 的 `pyproject.toml`，合并依赖到根目录的 `pyproject.toml`。
  - 只更新根 `pyproject.toml` 中的 `[tool.poetry.dependencies]` 和 `[tool.poetry.group.dev.dependencies]` 两个 section。
  - 会保留 UCloud 项目的包名、描述、作者、仓库地址、packages 等元信息。
  - 会跳过上游的 `e2b` 运行时依赖，因为 E2B 主 SDK 源码已经被同步进 `ucloud_sandbox/`，不应再依赖官方发布的 `e2b` 包。
  - 对已知版本冲突使用脚本中的显式覆盖规则；遇到未知依赖冲突时会报错，避免静默选择错误版本。

推荐手动同步顺序如下：

```bash
scripts/sync_upstreams.sh
python3 scripts/sync_dependencies.py
python3 scripts/hack.py
```

# UCloud 定制 Hack

`scripts/hack.py` 用于在上游代码同步完成后，重新应用本项目的 UCloud Sandbox 定制。上游同步会把 `ucloud_sandbox/` 恢复成 E2B 原始代码，因此每次运行 `scripts/sync_upstreams.sh` 之后，都需要手动运行：

```bash
python3 scripts/hack.py
```

`scripts/hack.py` 主要做这些事情：

- 将 `ucloud_sandbox/` 内部的主 SDK import 从 `e2b` 改为 `ucloud_sandbox`。
- 将 code interpreter 内部的 `e2b_code_interpreter` import 改为 `ucloud_sandbox.code_interpreter`。
- 将 docstring 和用户可见文档中的 `E2B` 改成 `UCloud Sandbox`。
- 将文档链接改成 `https://astraflow.ucloud.cn/docs/agent-sandbox/product/01-prerequisites`。
- 将环境变量从 `E2B_*` 改成 `UCLOUD_SANDBOX_*`。
- 默认关闭 API key 格式校验，并将校验逻辑改成仅检查非空。
- 将默认 domain 改成 `cn-wlcb.sandbox.ucloudai.com`。
- 额外支持 `UCLOUD_SANDBOX_REGION`，当该环境变量非空时，SDK 推导出的 domain 固定为 `{region}.sandbox.ucloudai.com`，并优先于 `UCLOUD_SANDBOX_DOMAIN`；显式传入的 `domain=` 参数仍然拥有最高优先级。
- 创建或恢复 `ucloud_sandbox/domain_config.py`，把 UCloud 专属 domain 推导逻辑集中在这个非上游 helper 中，避免把新增业务逻辑散落在从 E2B 同步来的文件里。
- 将 sandbox URL 固定为 `https://{port}-{sandbox_id}.{domain}` 的形式，不再走 `https://sandbox.<domain>`。
- 将 `metadata.version("e2b")` 改成 `metadata.version("ucloud_sandbox")`。
- 将 `publisher` 改成 `ucloud`。
- 将 User-Agent 改成 `ucloud-agentbox-sdk/{package_version}`。
- 将默认 base image 改成 `uhub.service.ucloud.cn/agentbox/e2bdev/base:latest`。
- 保留协议 header `E2B-Traffic-Access-Token` 不变，因为它属于服务端兼容协议，不是品牌文案。

验证 hack 是否成功时，至少要做下面几类检查：

```bash
rg -n '\bfrom e2b\b|\bimport e2b\b|e2b_code_interpreter|E2B_[A-Z0-9_]+|https://e2b\.dev|e2b\.app|e2b-python-sdk|metadata\.version\("e2b"\)|"publisher": "e2b"|api_key="e2b_|UCloud Sandbox Sandbox|UCloud Sandbox cloud sandbox' ucloud_sandbox
python3 -m compileall -q scripts/hack.py ucloud_sandbox e2b_connect
```

第一条命令应该没有输出。`E2B-Traffic-Access-Token` 和 `e2b_connect` 是例外：前者是协议 header，后者是上游 SDK 自带的连接 helper 包名，不属于要清理的品牌残留。

文档和 UCloud 专属 helper 也要人工快速过一遍，尤其是 `ucloud_sandbox/__init__.py`、`ucloud_sandbox/domain_config.py`、`ucloud_sandbox/code_interpreter/*.py`、`ucloud_sandbox/sandbox_sync/main.py`、`ucloud_sandbox/sandbox_async/main.py` 和 `ucloud_sandbox/template/main.py`。目标不是机械替换，而是保证中文或英文文档读起来通顺，避免出现 `UCloud Sandbox Sandbox`、`UCloud Sandbox cloud sandbox` 这类重复或别扭表达。

# 开发注意事项

- 不要把 `upstream/` 当作主要开发目录；它只是上游源码快照。
- 对 SDK 行为的 UCloud 定制应发生在同步后的 `ucloud_sandbox/` 中，或通过可重复执行的脚本来完成。
- 如果新增的 UCloud 定制不适合直接写进上游同步文件，优先放到独立 helper 中，并让 `scripts/hack.py` 在同步后可重复创建或恢复它。
- 每次运行 `scripts/sync_upstreams.sh` 后，`ucloud_sandbox/` 会重新变成上游合并结果，之前手动改过但没有脚本化的 UCloud 定制可能会被覆盖；随后需要手动运行 `python3 scripts/hack.py`。
- 如果 `pyproject.toml` 被依赖同步脚本更新了，通常还需要根据需要重新生成 `poetry.lock`。

# 提交信息规范

- Git commit message 使用 Conventional Commits 风格：`type(scope): summary`。
- 常用 `type` 包括 `feat`、`fix`、`docs`、`test`、`refactor`、`chore`；新增 SDK 能力时优先使用 `feat`。
- `scope` 使用简短英文小写词标识影响范围，例如 `config`、`hack`、`docs`。
- `summary` 用简短英文动词短语，不以句号结尾，例如 `feat(config): add region-based sandbox domain`。
