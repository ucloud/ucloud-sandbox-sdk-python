from ucloud_sandbox.connection_config import ConnectionConfig
from ucloud_sandbox.domain_config import get_ucloud_sandbox_domain
from ucloud_sandbox.volume.connection_config import VolumeConnectionConfig


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
