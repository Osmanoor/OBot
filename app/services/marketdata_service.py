import requests
from typing import Optional, Dict, Any

from ..config import settings

class MarketDataService:
    """
    A service to interact with the Marketdata.app API.
    """
    BASE_URL = "https://api.marketdata.app/v1/"

    def __init__(self, api_token: str):
        if not api_token:
            raise ValueError("Marketdata API token is required.")
        self.api_token = api_token

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Private method to handle GET requests to the API.
        """
        if params is None:
            params = {}
        params["token"] = self.api_token
        
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Marketdata API: {e}")
            return {}

    def find_option_contract(self, symbol: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Finds the first valid option contract based on the provided criteria.
        Corresponds to the 'Search Options API' node in the main workflow.
        """
        endpoint = f"options/chain/{symbol}/"
        data = self._get(endpoint, params=payload)

        if not data or "optionSymbol" not in data or not data["optionSymbol"]:
            return None

        # Adapt the response to a more convenient structure
        option = {
            "symbol": data["optionSymbol"][0],
            "type": data["side"][0].upper(),
            "underlying": data["underlying"][0],
            "strike_price": data["strike"][0],
            "last_price": data["last"][0],
            "bid": data["bid"][0],
            "ask": data["ask"][0],
            "mid": (data["bid"][0] + data["ask"][0]) / 2,
            "volume": data["volume"][0],
            "open_interest": data["openInterest"][0],
            "underlying_price": data["underlyingPrice"][0],
            "expiration_date": data["expiration"][0] # Unix timestamp
        }
        return option

    def get_option_quote(self, underlying_symbol: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Gets the latest quote for a specific option by fetching the chain and taking the first result.
        This is used for faster price updates as the /chain endpoint has less delay.
        """
        # Ensure the query is limited to the single, exact contract we want.
        params["limit"] = 1
        endpoint = f"options/chain/{underlying_symbol}/"
        data = self._get(endpoint, params=params)

        if not data or "optionSymbol" not in data or not data["optionSymbol"]:
            return None
            
        quote = {
            "last": data["last"][0],
            "bid": data["bid"][0],
            "ask": data["ask"][0],
            "mid": (data["bid"][0] + data["ask"][0]) / 2,
            "volume": data["volume"][0],
            "underlying_price": data["underlyingPrice"][0]
        }
        return quote

# Create a single instance of the service to be used throughout the app
marketdata_service = MarketDataService(api_token=settings.MARKETDATA_API_TOKEN)