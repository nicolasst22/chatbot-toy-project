import pytest
from app.services.router import AgentRouter

@pytest.mark.parametrize("message", [
    "cuanto cuesta",
    "¿Cuánto cuesta la RTX 4060?"
    "tienen stock",
    "¿Tienen stock del Ryzen 7?"
    "quiero comprar",
])
def test_rounting_sales(message):
    assert AgentRouter()._by_rules(message) == "sales"

@pytest.mark.parametrize("message", [
    "quiero hacer una devolución",
    "tiene garantia?",
])
def test_rounting_policies(message):
    assert AgentRouter()._by_rules(message) == "policies"

@pytest.mark.parametrize("message", [
    "Que socket tiene el ryzen 7?",
    "cuanto dura la garantia?",
])
def test_rounting_llm(message):
    assert AgentRouter()._by_rules(message) is None