from mcp.server.fastmcp import FastMCP
from pydantic import Field
import requests

mcp = FastMCP("product_mcp_server", host="0.0.0.0", port=8001)

@mcp.tool(
    name="currency_exchange_rate",
    description="Returns the rate between two currencies to convert prices from one currency into anonther. (e.g. USD to ARS)"
)
def currency_exchange_rate(
    currency_origin: str = Field(description="ISO 4217 currency code of the currency to convert from (e.g. USD)"),
    currency_destination: str = Field(description="ISO 4217 currency code of the currency to convert to (e.g. ARS)")
) :
    response = requests.get(f"https://api.frankfurter.dev/v2/rates?base={currency_origin.lower()}&quotes={currency_destination.lower()}")
    data = response.json()
    return  data[0]["rate"]


if __name__ == "__main__":
    mcp.run(transport="streamable-http")