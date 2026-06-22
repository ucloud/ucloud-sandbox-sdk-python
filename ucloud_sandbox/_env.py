import os


def setup() -> None:
    """Map UCLOUD_SANDBOX_* environment variables to E2B_* equivalents.

    Priority: existing E2B_* vars > UCLOUD_SANDBOX_* vars > defaults.
    """
    # API Key
    if "E2B_API_KEY" not in os.environ and "UCLOUD_SANDBOX_API_KEY" in os.environ:
        os.environ["E2B_API_KEY"] = os.environ["UCLOUD_SANDBOX_API_KEY"]

    # Domain: UCLOUD_SANDBOX_DOMAIN > UCLOUD_SANDBOX_REGION > default region cn-wlcb
    if "E2B_DOMAIN" not in os.environ:
        domain = os.environ.get("UCLOUD_SANDBOX_DOMAIN")
        if not domain:
            region = os.environ.get("UCLOUD_SANDBOX_REGION", "cn-wlcb")
            domain = f"{region}.sandbox.ucloudai.com"
        os.environ["E2B_DOMAIN"] = domain

    # API URL
    if "E2B_API_URL" not in os.environ and "UCLOUD_SANDBOX_API_URL" in os.environ:
        os.environ["E2B_API_URL"] = os.environ["UCLOUD_SANDBOX_API_URL"]

    # UCloud API keys have a different format from e2b; disable format validation by default
    if "E2B_VALIDATE_API_KEY" not in os.environ:
        os.environ["E2B_VALIDATE_API_KEY"] = "false"
