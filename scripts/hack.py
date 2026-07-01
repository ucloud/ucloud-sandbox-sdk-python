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

    text = text.replace("e2bdev/base:latest", BASE_IMAGE)
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
        text = text.replace(
            "from ucloud_sandbox.sandbox_domains import is_supported_sandbox_domain\n",
            "",
        )
        text = text.replace(
            'return os.getenv("UCLOUD_SANDBOX_DOMAIN") or "cn-wlcb.sandbox.ucloudai.com"',
            f'return os.getenv("UCLOUD_SANDBOX_DOMAIN") or "{DEFAULT_DOMAIN}"',
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
            '        sandbox_domain = sandbox_domain or self.domain\n'
            '        if is_supported_sandbox_domain(sandbox_domain):\n'
            '            return f"https://sandbox.{sandbox_domain}"\n\n'
            '        return f"https://{self.get_host(sandbox_id, sandbox_domain, self.envd_port)}"',
            '        sandbox_domain = sandbox_domain or self.domain\n'
            '        return f"https://{self.get_host(sandbox_id, sandbox_domain, self.envd_port)}"',
        )

    if path == PACKAGE_DIR / "volume" / "connection_config.py":
        text = text.replace(
            'return os.getenv("UCLOUD_SANDBOX_DOMAIN") or "cn-wlcb.sandbox.ucloudai.com"',
            f'return os.getenv("UCLOUD_SANDBOX_DOMAIN") or "{DEFAULT_DOMAIN}"',
        )

    if path == PACKAGE_DIR / "sandbox_domains.py":
        text = re.sub(
            r"SUPPORTED_SANDBOX_DOMAINS = \(.*?\)",
            f'SUPPORTED_SANDBOX_DOMAINS = ("{DEFAULT_DOMAIN}",)',
            text,
            flags=re.DOTALL,
        )

    return text


def patch_file(path: Path) -> bool:
    original = path.read_text()
    text = original.replace(TRAFFIC_HEADER, TRAFFIC_HEADER_PLACEHOLDER)

    text = replace_imports(text)
    text = replace_env_vars(text)
    text = replace_branding(text)
    text = patch_api_key_validation(path, text)
    text = patch_connection_config(path, text)

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

    print(f"Applied UCloud Sandbox hacks to {len(changed)} files.")
    for path in changed:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
