import os


DEFAULT_DOMAIN = "cn-wlcb.sandbox.ucloudai.com"
REGION_ENV_VAR = "UCLOUD_SANDBOX_REGION"
DOMAIN_ENV_VAR = "UCLOUD_SANDBOX_DOMAIN"
DOMAIN_SUFFIX = "sandbox.ucloudai.com"


def get_ucloud_sandbox_domain() -> str:
    region = os.getenv(REGION_ENV_VAR, "").strip()
    if region:
        return f"{region}.{DOMAIN_SUFFIX}"

    return os.getenv(DOMAIN_ENV_VAR) or DEFAULT_DOMAIN
