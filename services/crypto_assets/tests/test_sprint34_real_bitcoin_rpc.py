"""B4: Tests for Real Bitcoin RPC connector (httpx + mempool.space)."""
from decimal import Decimal

import httpx
import pytest
import respx

from services.crypto_assets.connectors.real_rpc_base import RealBitcoinRPCConnector

RPC_URL = "https://mempool.example/api"


def test_without_rpc_url_returns_zero():
    c = RealBitcoinRPCConnector()
    assert c.fetch_balance("bc1qxyz", "BTC") == Decimal("0")


@respx.mock
def test_btc_balance_converts_satoshi_to_btc():
    respx.get(f"{RPC_URL}/address/bc1qxyz").mock(return_value=httpx.Response(200, json={
        "address": "bc1qxyz",
        "chain_stats": {"funded_txo_sum": 150000000, "spent_txo_sum": 50000000},
        "mempool_stats": {"funded_txo_sum": 0, "spent_txo_sum": 0},
    }))
    c = RealBitcoinRPCConnector(rpc_url=RPC_URL)
    assert c.fetch_balance("bc1qxyz", "BTC") == Decimal("1")


@respx.mock
def test_non_btc_token_returns_zero_without_http_call():
    route = respx.get(f"{RPC_URL}/address/bc1qxyz")
    c = RealBitcoinRPCConnector(rpc_url=RPC_URL)
    assert c.fetch_balance("bc1qxyz", "USDC") == Decimal("0")
    assert route.call_count == 0


@respx.mock
def test_http_error_raises_runtime_error():
    respx.get(f"{RPC_URL}/address/bc1qxyz").mock(return_value=httpx.Response(500, text="server error"))
    c = RealBitcoinRPCConnector(rpc_url=RPC_URL)
    with pytest.raises(httpx.HTTPStatusError):
        c.fetch_balance("bc1qxyz", "BTC")
