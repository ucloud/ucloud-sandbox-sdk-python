from e2b import ConnectionConfig


def test_api_url_defaults_correctly(monkeypatch):
    monkeypatch.setenv("AGENTBOX_DOMAIN", "")
    monkeypatch.delenv("AGENTBOX_REGION", raising=False)

    config = ConnectionConfig()
    assert config.api_url == "https://api.cn-wlcb.sandbox.ucloudai.com"


def test_api_url_in_args():
    config = ConnectionConfig(api_url="http://localhost:8080")
    assert config.api_url == "http://localhost:8080"


def test_api_url_in_env_var(monkeypatch):
    monkeypatch.setenv("AGENTBOX_API_URL", "http://localhost:8080")

    config = ConnectionConfig()
    assert config.api_url == "http://localhost:8080"


def test_api_url_has_correct_priority(monkeypatch):
    monkeypatch.setenv("AGENTBOX_API_URL", "http://localhost:1111")

    config = ConnectionConfig(api_url="http://localhost:8080")
    assert config.api_url == "http://localhost:8080"


def test_region_cn_wlcb(monkeypatch):
    monkeypatch.delenv("AGENTBOX_DOMAIN", raising=False)
    monkeypatch.setenv("AGENTBOX_REGION", "cn-wlcb")

    config = ConnectionConfig()
    assert config.domain == "cn-wlcb.sandbox.ucloudai.com"
    assert config.api_url == "https://api.cn-wlcb.sandbox.ucloudai.com"


def test_region_us_ca(monkeypatch):
    monkeypatch.delenv("AGENTBOX_DOMAIN", raising=False)
    monkeypatch.setenv("AGENTBOX_REGION", "us-ca")

    config = ConnectionConfig()
    assert config.domain == "us-ca.sandbox.ucloudai.com"
    assert config.api_url == "https://api.us-ca.sandbox.ucloudai.com"


def test_domain_takes_priority_over_region(monkeypatch):
    monkeypatch.setenv("AGENTBOX_DOMAIN", "custom.example.com")
    monkeypatch.setenv("AGENTBOX_REGION", "us-ca")

    config = ConnectionConfig()
    assert config.domain == "custom.example.com"
    assert config.api_url == "https://api.custom.example.com"


def test_domain_arg_takes_priority_over_region(monkeypatch):
    monkeypatch.setenv("AGENTBOX_REGION", "us-ca")

    config = ConnectionConfig(domain="override.example.com")
    assert config.domain == "override.example.com"


def test_default_region_is_cn_wlcb(monkeypatch):
    monkeypatch.delenv("AGENTBOX_DOMAIN", raising=False)
    monkeypatch.delenv("AGENTBOX_REGION", raising=False)

    config = ConnectionConfig()
    assert config.domain == "cn-wlcb.sandbox.ucloudai.com"
