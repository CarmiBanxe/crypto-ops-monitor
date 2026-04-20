"""Production-ready RPC connector interfaces.

B3: Real Ethereum RPC via httpx + JSON-RPC.
- eth_getBalance for native ETH (wei -> ETH)
- eth_call + balanceOf(address) for ERC-20 tokens (USDC, USDT, DAI)

Without rpc_url the connector stays in safe-stub mode returning Decimal("0").
"""
from __future__ import annotations

from decimal import Decimal
from typing import ClassVar, cast

import httpx

from services.crypto_assets.connectors.blockchain_base import BlockchainConnector


class RpcError(RuntimeError):
    """Raised when the JSON-RPC server returns an error object."""


class RealEthereumRPCConnector(BlockchainConnector):
    network_code = "ethereum"

    ERC20_CONTRACTS: ClassVar[dict[str, str]] = {
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "DAI":  "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    }
    ERC20_DECIMALS: ClassVar[dict[str, int]] = {
        "USDC": 6,
        "USDT": 6,
        "DAI": 18,
    }
    BALANCE_OF_SELECTOR: ClassVar[str] = "0x70a08231"

    def __init__(
        self,
        rpc_url: str | None = None,
        api_key: str | None = None,
        timeout_sec: float = 10.0,
    ) -> None:
        self.rpc_url = rpc_url
        self.api_key = api_key
        self._timeout = timeout_sec

    def fetch_balance(self, address: str, token_symbol: str) -> Decimal:
        if not self.rpc_url:
            return Decimal("0")
        symbol = token_symbol.upper()
        if symbol == "ETH":
            return self._fetch_eth_balance(address)
        if symbol in self.ERC20_CONTRACTS:
            return self._fetch_erc20_balance(address, symbol)
        return Decimal("0")

    def fetch_transactions(
        self, address: str, since: str | None = None
    ) -> list[dict]:
        return []

    def _fetch_eth_balance(self, address: str) -> Decimal:
        result = self._post_jsonrpc("eth_getBalance", [address, "latest"])
        wei = int(result, 16)
        return Decimal(wei) / Decimal(10**18)

    def _fetch_erc20_balance(self, address: str, symbol: str) -> Decimal:
        contract = self.ERC20_CONTRACTS[symbol]
        data = (
            self.BALANCE_OF_SELECTOR
            + address.lower().removeprefix("0x").rjust(64, "0")
        )
        result = self._post_jsonrpc(
            "eth_call",
            [{"to": contract, "data": data}, "latest"],
        )
        raw = int(result, 16)
        decimals = self.ERC20_DECIMALS[symbol]
        return Decimal(raw) / Decimal(10**decimals)

    def _post_jsonrpc(self, method: str, params: list) -> str:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(self.rpc_url, json=payload)  # type: ignore[arg-type]
            response.raise_for_status()
            data = response.json()
        if "error" in data:
            raise RpcError(f"RPC error: {data['error']}")
        return cast(str, data["result"])


class RealBitcoinRPCConnector(BlockchainConnector):
    """BTC via mempool.space-compatible REST: GET /address/{addr}.

    Balance = (chain_stats.funded - chain_stats.spent) / 1e8 satoshi.
    """

    network_code = "bitcoin"
    SATOSHI_PER_BTC: ClassVar[int] = 10**8

    def __init__(
        self,
        rpc_url: str | None = None,
        api_key: str | None = None,
        timeout_sec: float = 10.0,
    ) -> None:
        self.rpc_url = rpc_url
        self.api_key = api_key
        self._timeout = timeout_sec

    def fetch_balance(self, address: str, token_symbol: str) -> Decimal:
        if not self.rpc_url:
            return Decimal("0")
        if token_symbol.upper() != "BTC":
            return Decimal("0")
        return self._fetch_btc_balance(address)

    def fetch_transactions(
        self, address: str, since: str | None = None
    ) -> list[dict]:
        return []

    def _fetch_btc_balance(self, address: str) -> Decimal:
        url = f"{self.rpc_url}/address/{address}"
        with httpx.Client(timeout=self._timeout) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
        chain = data.get("chain_stats", {})
        funded = int(chain.get("funded_txo_sum", 0))
        spent = int(chain.get("spent_txo_sum", 0))
        satoshi = funded - spent
        return Decimal(satoshi) / Decimal(self.SATOSHI_PER_BTC)
