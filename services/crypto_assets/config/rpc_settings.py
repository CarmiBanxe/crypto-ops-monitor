from pydantic_settings import BaseSettings, SettingsConfigDict


class RpcSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")

    live_mode: bool = False
    eth_rpc_url: str | None = None
    eth_rpc_api_key: str | None = None
    btc_rpc_url: str | None = None
    btc_rpc_api_key: str | None = None
    rpc_timeout_sec: float = 10.0
    rpc_max_retries: int = 3

    def eth_configured(self) -> bool:
        return self.eth_rpc_url is not None

    def btc_configured(self) -> bool:
        return self.btc_rpc_url is not None


def get_rpc_settings() -> RpcSettings:
    return RpcSettings()
