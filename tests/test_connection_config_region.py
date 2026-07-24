from packaging.version import Version

from ucloud_sandbox.connection_config import ConnectionConfig
from ucloud_sandbox.domain_config import get_ucloud_sandbox_domain
from ucloud_sandbox.sandbox.main import SandboxBase
from ucloud_sandbox.volume.connection_config import VolumeConnectionConfig
from ucloud_sandbox.volume.volume_async import AsyncVolume
from ucloud_sandbox.volume.volume_sync import Volume


def test_region_env_overrides_domain_env(monkeypatch):
    monkeypatch.setenv("UCLOUD_SANDBOX_REGION", "cn-bj")
    monkeypatch.setenv("UCLOUD_SANDBOX_DOMAIN", "custom.example")
    monkeypatch.delenv("UCLOUD_SANDBOX_API_URL", raising=False)

    config = ConnectionConfig()

    assert get_ucloud_sandbox_domain() == "cn-bj.sandbox.ucloudai.com"
    assert config.domain == "cn-bj.sandbox.ucloudai.com"
    assert config.api_url == "https://api.cn-bj.sandbox.ucloudai.com"


def test_explicit_domain_has_priority_over_region_env(monkeypatch):
    monkeypatch.setenv("UCLOUD_SANDBOX_REGION", "cn-bj")

    config = ConnectionConfig(domain="custom.example")

    assert config.domain == "custom.example"
    assert config.api_url == "https://api.custom.example"


def test_volume_config_uses_region_env(monkeypatch):
    monkeypatch.setenv("UCLOUD_SANDBOX_REGION", "cn-sh2")
    monkeypatch.setenv("UCLOUD_SANDBOX_DOMAIN", "custom.example")
    monkeypatch.delenv("UCLOUD_SANDBOX_VOLUME_API_URL", raising=False)

    config = VolumeConnectionConfig()

    assert config.domain == "cn-sh2.sandbox.ucloudai.com"
    assert config.api_url == "https://api.cn-sh2.sandbox.ucloudai.com"


def test_insecure_http_supports_all_sandbox_urls(monkeypatch):
    monkeypatch.delenv("UCLOUD_SANDBOX_INSECURE_HTTP", raising=False)
    config = ConnectionConfig(
        domain="private.example",
        api_url="http://api.private.example",
        insecure_http=True,
    )

    sandbox = SandboxBase(
        sandbox_id="sandbox-id",
        sandbox_domain="private.example",
        envd_version=Version("0.1.0"),
        envd_access_token=None,
        traffic_access_token=None,
        connection_config=config,
    )

    assert config.api_url == "http://api.private.example"
    assert sandbox.envd_api_url == "http://49983-sandbox-id.private.example"
    assert sandbox.get_url(8080, "/health") == (
        "http://8080-sandbox-id.private.example/health"
    )
    assert sandbox.get_mcp_url() == "http://50005-sandbox-id.private.example/mcp"


def test_insecure_http_uses_environment(monkeypatch):
    monkeypatch.setenv("UCLOUD_SANDBOX_INSECURE_HTTP", "true")

    config = ConnectionConfig(domain="private.example")
    volume_config = VolumeConnectionConfig(domain="private.example")

    assert config.insecure_http is True
    assert config.sandbox_protocol == "http"
    assert config.api_url == "http://api.private.example"
    assert config.get_sandbox_url("sandbox-id", "private.example") == (
        "http://49983-sandbox-id.private.example"
    )
    assert volume_config.insecure_http is True
    assert volume_config.api_url == "http://api.private.example"


def test_secure_https_is_the_default(monkeypatch):
    monkeypatch.delenv("UCLOUD_SANDBOX_INSECURE_HTTP", raising=False)

    config = ConnectionConfig(domain="private.example")

    assert config.insecure_http is False
    assert config.sandbox_protocol == "https"
    assert config.api_url == "https://api.private.example"


def test_explicit_secure_http_setting_overrides_environment(monkeypatch):
    monkeypatch.setenv("UCLOUD_SANDBOX_INSECURE_HTTP", "true")

    config = ConnectionConfig(domain="private.example", insecure_http=False)

    assert config.insecure_http is False
    assert config.api_url == "https://api.private.example"


def test_insecure_http_is_propagated_to_per_call_config(monkeypatch):
    monkeypatch.delenv("UCLOUD_SANDBOX_INSECURE_HTTP", raising=False)
    config = ConnectionConfig(domain="private.example", insecure_http=True)

    per_call_config = ConnectionConfig(**config.get_api_params())

    assert per_call_config.insecure_http is True
    assert per_call_config.api_url == "http://api.private.example"
    assert per_call_config.get_sandbox_url("sandbox-id", "private.example") == (
        "http://49983-sandbox-id.private.example"
    )


def test_volume_instances_preserve_insecure_http_setting(monkeypatch):
    monkeypatch.delenv("UCLOUD_SANDBOX_INSECURE_HTTP", raising=False)
    volume = Volume(
        volume_id="volume-id",
        name="volume",
        domain="private.example",
        insecure_http=True,
    )
    async_volume = AsyncVolume(
        volume_id="volume-id",
        name="volume",
        domain="private.example",
        insecure_http=True,
    )

    assert volume._get_volume_config().api_url == "http://api.private.example"
    assert async_volume._get_volume_config().api_url == "http://api.private.example"
