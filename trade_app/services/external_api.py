from typing import Dict, Any

import aiohttp

from trade_app.core.config import settings


class ExternalDataService:
    """Service to fetch data from GLEIF API and extract required data from output."""

    def __init__(self):
        self.api_url = settings.GLEIF_API_URL

    async def fetch_external_data(self, lei: str) -> Dict[str, Any]:
       
        url = f"{self.api_url}?filter[lei]={lei}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    response_data = await response.json()
                    return response_data
            except aiohttp.ClientError as e:
                return {"data": []}

    @staticmethod
    def extract_required_data(response_data: Dict[str, Any]) -> Dict[str, Any]:
       
        result = {"legal_name": "", "bic": [], "country": ""}

        if not response_data.get("data"):
            return result

        data = response_data["data"][0]
        attributes = data.get("attributes", {})

        # Extract legal name
        entity = attributes.get("entity", {})
        legal_name = entity.get("legalName", {})
        result["legal_name"] = legal_name.get("name", "")

        # Extract BIC
        result["bic"] = attributes.get("bic", [])

        # Extract country
        legal_address = entity.get("legalAddress", {})
        result["country"] = legal_address.get("country", "")

        return result
