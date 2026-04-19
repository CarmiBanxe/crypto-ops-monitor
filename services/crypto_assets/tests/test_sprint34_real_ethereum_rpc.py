"""B3: Tests for Real Ethereum RPC connector (httpx + JSON-RPC)."""
from decimal import Decimal

import httpx
import pytest
import respx

from services.crypto_assets.connectors.real_rpc_base import RealEthereumRPCConnector

RPC_URL = "https://eth.example/v1"


def test_without_rpc_url_returns_zero_for_eth_and_erc20():
    c = RealEthereumRPCConnector()
    assert c.fetch_balance("0xabc", "ETH") == Decimal("0")
    assert c.fetch_balance("0xabc", "USDC") == Decimal("0")


@respx.mock
def test_eth_balance_converts_wei_to_eth():
    respx.post(RPC_URL).mock(return_value=httpx.Response(200, json={
        "jsonrpc": "2.0", "id": 1,
        "result": "0x16345785d8a0000",  # 0.1 ETH in wei
    }))
    c = RealEthereumRPCConnector(rpc_url=RPC_URL)
    assert c.fetch_balance("0x1234", "ETH") == Decimal("0.1")


@respx.mock
def test_erc20_usdc_balance_with_6_decimals():
    respx.post(RPC_URL).mock(return_value=httpx.Response(200, json={
        "jsonrpc": "2.0", "id": 1,
        "result": "0x" + format(500_000_000, "x"),  # 500 USDC with 6 decimals
    }))
    c = RealEthereumRPCConnector(rpc_url=RPC_URL)
    assert c.fetch_balance("0x1234", "USDC") == Decimal("500")


@respx.mock
def test_unknown_token_returns_zero_without_http_call():
    route = respx.post(RPC_URL)
    c = RealEthereumRPCConnector(rpc_url=RPC_URL)
    assert c.fetch_balance("0xabc", "SHIB") == Decimal("0")
    assert route.call_count == 0


@respx.mock
def test_jsonrpc_error_raises_runtime_error():
    respx.post(RPC_URL).mock(return_value=httpx.Response(200, json={
        "jsonrpc": "2.0", "id": 1,
        "error": {"code": -32600, "message": "Invalid request"},
    }))
    c = RealEthereumRPCConnector(rpc_url=RPC_URL)
    with pytest.raises(RuntimeError, match="RPC error"):
        c.fetch_balance("0x1234", "ETH")
