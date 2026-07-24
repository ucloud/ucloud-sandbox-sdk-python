#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(
    subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
)
PACKAGE_DIR = REPO_ROOT / "ucloud_sandbox"
DOCS_URL = "https://astraflow.ucloud.cn/docs/agent-sandbox/product/01-prerequisites"
DEFAULT_DOMAIN = "cn-wlcb.sandbox.ucloudai.com"
BASE_IMAGE = "uhub.service.ucloud.cn/agentbox/e2bdev/base:latest"
DOMAIN_CONFIG_PATH = PACKAGE_DIR / "domain_config.py"
DOMAIN_CONFIG_IMPORT = (
    "from ucloud_sandbox.domain_config import get_ucloud_sandbox_domain\n"
)
DOMAIN_CONFIG_SOURCE = f'''import os


DEFAULT_DOMAIN = "{DEFAULT_DOMAIN}"
REGION_ENV_VAR = "UCLOUD_SANDBOX_REGION"
DOMAIN_ENV_VAR = "UCLOUD_SANDBOX_DOMAIN"
DOMAIN_SUFFIX = "sandbox.ucloudai.com"


def get_ucloud_sandbox_domain() -> str:
    region = os.getenv(REGION_ENV_VAR, "").strip()
    if region:
        return f"{{region}}.{{DOMAIN_SUFFIX}}"

    return os.getenv(DOMAIN_ENV_VAR) or DEFAULT_DOMAIN
'''

TRAFFIC_HEADER = "E2B-Traffic-Access-Token"
TRAFFIC_HEADER_PLACEHOLDER = "__UCLOUD_SANDBOX_KEEP_TRAFFIC_ACCESS_TOKEN__"

ENV_REPLACEMENTS = {
    "E2B_MAX_KEEPALIVE_CONNECTIONS": "UCLOUD_SANDBOX_MAX_KEEPALIVE_CONNECTIONS",
    "E2B_KEEPALIVE_EXPIRY": "UCLOUD_SANDBOX_KEEPALIVE_EXPIRY",
    "E2B_CONNECTION_RETRIES": "UCLOUD_SANDBOX_CONNECTION_RETRIES",
    "E2B_VALIDATE_API_KEY": "UCLOUD_SANDBOX_VALIDATE_API_KEY",
    "E2B_VOLUME_API_URL": "UCLOUD_SANDBOX_VOLUME_API_URL",
    "E2B_MAX_CONNECTIONS": "UCLOUD_SANDBOX_MAX_CONNECTIONS",
    "E2B_SANDBOX_URL": "UCLOUD_SANDBOX_URL",
    "E2B_ACCESS_TOKEN": "UCLOUD_SANDBOX_ACCESS_TOKEN",
    "E2B_API_KEY": "UCLOUD_SANDBOX_API_KEY",
    "E2B_API_URL": "UCLOUD_SANDBOX_API_URL",
    "E2B_DOMAIN": "UCLOUD_SANDBOX_DOMAIN",
    "E2B_DEBUG": "UCLOUD_SANDBOX_DEBUG",
}


def replace_imports(text: str) -> str:
    text = re.sub(r"(?m)(^|\s)from e2b(?=[.\s])", r"\1from ucloud_sandbox", text)
    text = re.sub(r"(?m)(^|\s)import e2b(?=\s|$)", r"\1import ucloud_sandbox", text)
    text = text.replace(
        "from e2b_code_interpreter.",
        "from ucloud_sandbox.code_interpreter.",
    )
    text = text.replace(
        "from e2b_code_interpreter import",
        "from ucloud_sandbox.code_interpreter import",
    )
    text = text.replace(
        "import e2b_code_interpreter",
        "import ucloud_sandbox.code_interpreter",
    )
    return text


def replace_branding(text: str) -> str:
    text = text.replace("https://e2b.dev/dashboard?tab=keys", DOCS_URL)
    text = text.replace("https://e2b.dev/docs", DOCS_URL)

    text = text.replace('metadata.version("e2b")', 'metadata.version("ucloud_sandbox")')
    text = text.replace('"publisher": "e2b"', '"publisher": "ucloud"')
    text = text.replace("e2b-python-sdk", "ucloud-agentbox-sdk")

    text = text.replace("e2b.app", DEFAULT_DOMAIN)
    text = text.replace("e2b.dev", DEFAULT_DOMAIN)
    text = text.replace("e2b.pro", DEFAULT_DOMAIN)
    text = text.replace("e2b-staging.dev", DEFAULT_DOMAIN)

    text = re.sub(r"(?<!/)e2bdev/base:latest", BASE_IMAGE, text)
    text = text.replace('"e2bdev/base"', f'"{BASE_IMAGE}"')
    text = text.replace('api_key="e2b_..."', 'api_key="..."')

    text = re.sub(r"\bE2B\b", "UCloud Sandbox", text)
    text = text.replace("UCloud Sandbox Sandbox", "UCloud Sandbox")
    text = text.replace("UCloud Sandbox cloud sandbox", "UCloud Sandbox")
    return text


def replace_env_vars(text: str) -> str:
    for old, new in ENV_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def add_domain_config_import(text: str) -> str:
    if DOMAIN_CONFIG_IMPORT in text:
        return text

    metadata_import = "from ucloud_sandbox.api.metadata import package_version\n"
    if metadata_import not in text:
        raise RuntimeError("Failed to find metadata import for domain config patch")

    return text.replace(metadata_import, metadata_import + DOMAIN_CONFIG_IMPORT)


def patch_api_key_validation(path: Path, text: str) -> str:
    if path != PACKAGE_DIR / "api" / "__init__.py":
        return text

    replacement = f'''_API_KEY_PATTERN = re.compile(r"\\A.+\\Z")


def validate_api_key(api_key: str) -> None:
    """Validate that a UCloud Sandbox API key is not empty."""
    if not _API_KEY_PATTERN.match(api_key):
        raise AuthenticationException(
            "Invalid API key format. Set `UCLOUD_SANDBOX_API_KEY` "
            "or pass `api_key` directly. See {DOCS_URL}."
        )
'''

    text, count = re.subn(
        r"_API_KEY_PATTERN = .*?\n\n\ndef validate_api_key\(api_key: str\) -> None:\n.*?(?=\n\nclass ApiClient)",
        lambda _: replacement,
        text,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError(f"Failed to patch API key validation in {path}")
    return text


def patch_connection_config(path: Path, text: str) -> str:
    if path == PACKAGE_DIR / "connection_config.py":
        text = add_domain_config_import(text)
        text = text.replace(
            "from ucloud_sandbox.sandbox_domains import is_supported_sandbox_domain\n",
            "",
        )
        text = text.replace(
            'return os.getenv("UCLOUD_SANDBOX_DOMAIN") or "cn-wlcb.sandbox.ucloudai.com"',
            "return get_ucloud_sandbox_domain()",
        )
        text = text.replace(
            'return os.getenv("UCLOUD_SANDBOX_VALIDATE_API_KEY", "true").lower() != "false"',
            'return os.getenv("UCLOUD_SANDBOX_VALIDATE_API_KEY", "false").lower() == "true"',
        )
        text = text.replace(
            "    default `e2b_` format. Defaults to `UCLOUD_SANDBOX_VALIDATE_API_KEY` environment\n"
            "    variable or `True`.",
            "    validation is disabled by default. Set `UCLOUD_SANDBOX_VALIDATE_API_KEY=true`\n"
            "    to enable a non-empty API key check.",
        )
        text = text.replace(
            "UCloud Sandbox domain to use for authentication, defaults to `UCLOUD_SANDBOX_DOMAIN` environment variable.",
            "UCloud Sandbox domain to use for authentication, defaults to `UCLOUD_SANDBOX_REGION`, `UCLOUD_SANDBOX_DOMAIN`, or the default UCloud Sandbox domain.",
        )
        text = text.replace(
            "        sandbox_domain = sandbox_domain or self.domain\n"
            "        if is_supported_sandbox_domain(sandbox_domain):\n"
            '            return f"https://sandbox.{sandbox_domain}"\n\n'
            '        return f"https://{self.get_host(sandbox_id, sandbox_domain, self.envd_port)}"',
            "        sandbox_domain = sandbox_domain or self.domain\n"
            '        return f"https://{self.get_host(sandbox_id, sandbox_domain, self.envd_port)}"',
        )

    if path == PACKAGE_DIR / "volume" / "connection_config.py":
        text = add_domain_config_import(text)
        text = text.replace(
            'return os.getenv("UCLOUD_SANDBOX_DOMAIN") or "cn-wlcb.sandbox.ucloudai.com"',
            "return get_ucloud_sandbox_domain()",
        )
        text = text.replace(
            "Domain to use for the volume API, defaults to `UCLOUD_SANDBOX_DOMAIN` or `cn-wlcb.sandbox.ucloudai.com`.",
            "Domain to use for the volume API, defaults to `UCLOUD_SANDBOX_REGION`, `UCLOUD_SANDBOX_DOMAIN`, or the default UCloud Sandbox domain.",
        )

    if path == PACKAGE_DIR / "sandbox_domains.py":
        text = re.sub(
            r"SUPPORTED_SANDBOX_DOMAINS = \(.*?\)",
            f'SUPPORTED_SANDBOX_DOMAINS = ("{DEFAULT_DOMAIN}",)',
            text,
            flags=re.DOTALL,
        )

    return text


def replace_once(path: Path, text: str, old: str, new: str) -> str:
    if old not in text:
        raise RuntimeError(f"Failed to apply insecure HTTP patch in {path}")
    return text.replace(old, new, 1)


def patch_insecure_http(path: Path, text: str) -> str:
    if path == PACKAGE_DIR / "connection_config.py":
        if "    insecure_http: Optional[bool]\n" in text:
            return text

        text = replace_once(
            path,
            text,
            "    sandbox_url: Optional[str]\n"
            '    """URL to connect to sandbox, defaults to `UCLOUD_SANDBOX_URL` environment variable."""\n',
            "    sandbox_url: Optional[str]\n"
            '    """URL to connect to sandbox, defaults to `UCLOUD_SANDBOX_URL` environment variable."""\n\n'
            "    insecure_http: Optional[bool]\n"
            '    """Whether to use HTTP instead of HTTPS, defaults to `UCLOUD_SANDBOX_INSECURE_HTTP`."""\n',
        )
        text = text.replace(
            '    """URL to use for the API, defaults to `https://api.<domain>`. For internal use only."""',
            '    """URL to use for the API, defaults to `<protocol>://api.<domain>`. For internal use only."""',
        )
        text = replace_once(
            path,
            text,
            '    def _sandbox_url():\n        return os.getenv("UCLOUD_SANDBOX_URL")\n',
            "    def _sandbox_url():\n"
            '        return os.getenv("UCLOUD_SANDBOX_URL")\n\n'
            "    @staticmethod\n"
            "    def _insecure_http():\n"
            '        return os.getenv("UCLOUD_SANDBOX_INSECURE_HTTP", "false").lower() == "true"\n',
        )
        text = replace_once(
            path,
            text,
            "        sandbox_url: Optional[str] = None,\n"
            "        access_token: Optional[str] = None,\n",
            "        sandbox_url: Optional[str] = None,\n"
            "        insecure_http: Optional[bool] = None,\n"
            "        access_token: Optional[str] = None,\n",
        )
        text = replace_once(
            path,
            text,
            "        self.api_url = (\n"
            "            api_url\n"
            "            or ConnectionConfig._api_url()\n"
            '            or ("http://localhost:3000" if self.debug else f"https://api.{self.domain}")\n'
            "        )\n\n"
            "        self._sandbox_url: Optional[str] = (\n"
            "            sandbox_url or ConnectionConfig._sandbox_url()\n"
            "        )\n",
            "        self._sandbox_url: Optional[str] = sandbox_url or ConnectionConfig._sandbox_url()\n"
            "        self.insecure_http = (\n"
            "            True\n"
            "            if self.debug\n"
            "            else (\n"
            "                insecure_http\n"
            "                if insecure_http is not None\n"
            "                else ConnectionConfig._insecure_http()\n"
            "            )\n"
            "        )\n"
            '        self.sandbox_protocol = "http" if self.insecure_http else "https"\n\n'
            "        self.api_url = (\n"
            "            api_url\n"
            "            or ConnectionConfig._api_url()\n"
            "            or (\n"
            '                "http://localhost:3000"\n'
            "                if self.debug\n"
            '                else f"{self.sandbox_protocol}://api.{self.domain}"\n'
            "            )\n"
            "        )\n",
        )
        text = replace_once(
            path,
            text,
            "        if self.debug:\n"
            '            return f"http://{self.get_host(sandbox_id, sandbox_domain, self.envd_port)}"\n\n'
            "        sandbox_domain = sandbox_domain or self.domain\n"
            '        return f"https://{self.get_host(sandbox_id, sandbox_domain, self.envd_port)}"\n',
            "        sandbox_domain = sandbox_domain or self.domain\n"
            '        return f"{self.sandbox_protocol}://{self.get_host(sandbox_id, sandbox_domain, self.envd_port)}"\n',
        )
        text = replace_once(
            path,
            text,
            "        if self.debug:\n"
            '            return f"http://{self.get_host(sandbox_id, sandbox_domain, self.envd_port)}"\n\n'
            '        return f"https://{self.get_host(sandbox_id, sandbox_domain, self.envd_port)}"\n',
            '        return f"{self.sandbox_protocol}://{self.get_host(sandbox_id, sandbox_domain, self.envd_port)}"\n',
        )
        text = replace_once(
            path,
            text,
            '        sandbox_url = opts.get("sandbox_url")\n',
            '        sandbox_url = opts.get("sandbox_url")\n'
            '        insecure_http = opts.get("insecure_http")\n',
        )
        text = replace_once(
            path,
            text,
            "                sandbox_url=(\n"
            "                    sandbox_url\n"
            "                    if sandbox_url is not None\n"
            "                    else cast(Optional[str], self._sandbox_url)\n"
            "                ),\n",
            "                sandbox_url=(\n"
            "                    sandbox_url\n"
            "                    if sandbox_url is not None\n"
            "                    else cast(Optional[str], self._sandbox_url)\n"
            "                ),\n"
            "                insecure_http=(\n"
            "                    insecure_http\n"
            "                    if insecure_http is not None\n"
            "                    else self.insecure_http\n"
            "                ),\n",
        )

    if path == PACKAGE_DIR / "volume" / "connection_config.py":
        if "    insecure_http: Optional[bool]\n" in text:
            return text

        text = replace_once(
            path,
            text,
            "    debug: Optional[bool]\n"
            '    """Whether to use debug mode, defaults to `UCLOUD_SANDBOX_DEBUG` environment variable."""\n',
            "    debug: Optional[bool]\n"
            '    """Whether to use debug mode, defaults to `UCLOUD_SANDBOX_DEBUG` environment variable."""\n\n'
            "    insecure_http: Optional[bool]\n"
            '    """Whether to use HTTP instead of HTTPS, defaults to `UCLOUD_SANDBOX_INSECURE_HTTP`."""\n',
        )
        text = text.replace(
            '    """URL to use for the volume API, defaults to `UCLOUD_SANDBOX_VOLUME_API_URL` or `https://api.<domain>`."""',
            '    """URL to use for the volume API, defaults to `UCLOUD_SANDBOX_VOLUME_API_URL` or `<protocol>://api.<domain>`."""',
        )
        text = replace_once(
            path,
            text,
            "    def _volume_api_url():\n"
            '        return os.getenv("UCLOUD_SANDBOX_VOLUME_API_URL")\n',
            "    def _volume_api_url():\n"
            '        return os.getenv("UCLOUD_SANDBOX_VOLUME_API_URL")\n\n'
            "    @staticmethod\n"
            "    def _insecure_http():\n"
            '        return os.getenv("UCLOUD_SANDBOX_INSECURE_HTTP", "false").lower() == "true"\n',
        )
        text = replace_once(
            path,
            text,
            "        domain: Optional[str] = None,\n"
            "        debug: Optional[bool] = None,\n"
            "        token: Optional[str] = None,\n",
            "        domain: Optional[str] = None,\n"
            "        debug: Optional[bool] = None,\n"
            "        insecure_http: Optional[bool] = None,\n"
            "        token: Optional[str] = None,\n",
        )
        text = replace_once(
            path,
            text,
            "        self.domain = domain or self._domain()\n"
            "        self.debug = debug if debug is not None else self._debug()\n\n"
            "        self.api_url = (\n"
            "            api_url\n"
            "            or self._volume_api_url()\n"
            '            or ("http://localhost:8080" if self.debug else f"https://api.{self.domain}")\n'
            "        )\n",
            "        self.domain = domain or self._domain()\n"
            "        self.debug = debug if debug is not None else self._debug()\n"
            "        self.insecure_http = (\n"
            "            True\n"
            "            if self.debug\n"
            "            else (\n"
            "                insecure_http\n"
            "                if insecure_http is not None\n"
            "                else self._insecure_http()\n"
            "            )\n"
            "        )\n"
            '        protocol = "http" if self.insecure_http else "https"\n\n'
            "        self.api_url = (\n"
            "            api_url\n"
            "            or self._volume_api_url()\n"
            "            or (\n"
            '                "http://localhost:8080"\n'
            "                if self.debug\n"
            '                else f"{protocol}://api.{self.domain}"\n'
            "            )\n"
            "        )\n",
        )
        text = replace_once(
            path,
            text,
            '        debug = opts.get("debug")\n',
            '        debug = opts.get("debug")\n'
            '        insecure_http = opts.get("insecure_http")\n',
        )
        text = replace_once(
            path,
            text,
            "                debug=debug if debug is not None else self.debug,\n",
            "                debug=debug if debug is not None else self.debug,\n"
            "                insecure_http=(\n"
            "                    insecure_http\n"
            "                    if insecure_http is not None\n"
            "                    else self.insecure_http\n"
            "                ),\n",
        )

    if path == PACKAGE_DIR / "sandbox" / "main.py":
        if '    def get_url(self, port: int, path: str = "") -> str:\n' in text:
            return text

        text = replace_once(
            path,
            text,
            "        return self.connection_config.get_host(\n"
            "            self.sandbox_id, self.sandbox_domain, port\n"
            "        )\n\n"
            "    def get_mcp_url(self) -> str:\n",
            "        return self.connection_config.get_host(\n"
            "            self.sandbox_id, self.sandbox_domain, port\n"
            "        )\n\n"
            '    def get_url(self, port: int, path: str = "") -> str:\n'
            '        """\n'
            "        Get the HTTP(S) URL for a sandbox port.\n\n"
            "        :param port: Port to connect to\n"
            "        :param path: Optional URL path, including the leading slash\n\n"
            "        :return: URL for connecting to the sandbox port\n"
            '        """\n'
            '        return f"{self.connection_config.sandbox_protocol}://{self.get_host(port)}{path}"\n\n'
            "    def get_mcp_url(self) -> str:\n",
        )
        text = replace_once(
            path,
            text,
            '        return f"https://{self.get_host(self.mcp_port)}/mcp"\n',
            '        return self.get_url(self.mcp_port, "/mcp")\n',
        )

    if path in {
        PACKAGE_DIR / "code_interpreter" / "code_interpreter_sync.py",
        PACKAGE_DIR / "code_interpreter" / "code_interpreter_async.py",
    }:
        old = (
            "        return f\"{'http' if self.connection_config.debug else 'https'}://"
            '{self.get_host(JUPYTER_PORT)}"\n'
        )
        if old in text:
            text = text.replace(old, "        return self.get_url(JUPYTER_PORT)\n", 1)

    if path == PACKAGE_DIR / "desktop" / "main.py":
        text = text.replace(
            'self._url = f"https://{desktop.get_host(self._port)}/vnc.html"',
            'self._url = desktop.get_url(self._port, "/vnc.html")',
        )
        text = text.replace(
            'self._url = f"https://{self.__desktop.get_host(self._port)}/vnc.html"',
            'self._url = self.__desktop.get_url(self._port, "/vnc.html")',
        )

    if path in {
        PACKAGE_DIR / "volume" / "volume_sync.py",
        PACKAGE_DIR / "volume" / "volume_async.py",
    }:
        if "        self._insecure_http = insecure_http\n" in text:
            return text

        text = replace_once(
            path,
            text,
            "        domain: Optional[str] = None,\n"
            "        debug: Optional[bool] = None,\n"
            "        proxy: Optional[ProxyTypes] = None,\n",
            "        domain: Optional[str] = None,\n"
            "        debug: Optional[bool] = None,\n"
            "        insecure_http: Optional[bool] = None,\n"
            "        proxy: Optional[ProxyTypes] = None,\n",
        )
        text = replace_once(
            path,
            text,
            "        self._domain = domain\n"
            "        self._debug = debug\n"
            "        self._proxy = proxy\n",
            "        self._domain = domain\n"
            "        self._debug = debug\n"
            "        self._insecure_http = insecure_http\n"
            "        self._proxy = proxy\n",
        )
        text = replace_once(
            path,
            text,
            '            debug=opts.get("debug") if opts.get("debug") is not None else self._debug,\n',
            '            debug=opts.get("debug") if opts.get("debug") is not None else self._debug,\n'
            "            insecure_http=(\n"
            '                opts.get("insecure_http")\n'
            '                if opts.get("insecure_http") is not None\n'
            "                else self._insecure_http\n"
            "            ),\n",
        )
        text = text.replace(
            "            debug=config.debug,\n            proxy=config.proxy,\n",
            "            debug=config.debug,\n"
            "            insecure_http=config.insecure_http,\n"
            "            proxy=config.proxy,\n",
        )

    return text


def ensure_domain_config() -> bool:
    original = DOMAIN_CONFIG_PATH.read_text() if DOMAIN_CONFIG_PATH.exists() else None
    if original == DOMAIN_CONFIG_SOURCE:
        return False

    DOMAIN_CONFIG_PATH.write_text(DOMAIN_CONFIG_SOURCE)
    return True


def patch_file(path: Path) -> bool:
    original = path.read_text()
    text = original.replace(TRAFFIC_HEADER, TRAFFIC_HEADER_PLACEHOLDER)

    text = replace_imports(text)
    text = replace_env_vars(text)
    text = replace_branding(text)
    text = patch_api_key_validation(path, text)
    text = patch_connection_config(path, text)
    text = patch_insecure_http(path, text)

    text = text.replace(TRAFFIC_HEADER_PLACEHOLDER, TRAFFIC_HEADER)

    if text != original:
        path.write_text(text)
        return True
    return False


def main() -> int:
    if not PACKAGE_DIR.is_dir():
        raise RuntimeError(f"Package directory not found: {PACKAGE_DIR}")

    changed = []
    for path in sorted(PACKAGE_DIR.rglob("*.py")):
        if patch_file(path):
            changed.append(path.relative_to(REPO_ROOT).as_posix())

    if ensure_domain_config():
        changed.append(DOMAIN_CONFIG_PATH.relative_to(REPO_ROOT).as_posix())

    print(f"Applied UCloud Sandbox hacks to {len(changed)} files.")
    for path in changed:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
