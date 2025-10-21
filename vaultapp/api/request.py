import logging
import time
from http import HTTPMethod

import requests

from vaultapp.api.region import ApiRegion

logger = logging.getLogger(__name__)

class ApiRequest:
    def __init__(self, auth_key: str, region: ApiRegion=ApiRegion.NA):
        self.region = region
        self.auth_key = auth_key


    def exec(self, endpoint: str, method: HTTPMethod, data=None):
        headers = {
            'Authorization': f'Bearer {self.auth_key}'
        }

        url = f"{self.region}{endpoint}"

        response = requests.request(method, url, headers=headers, data=data)

        if response.status_code == 429:
            wait_time = 12
            logger.info(f"Rate limit exceeded. Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)
            return self.exec(endpoint, method, data)

        # Handle errors without an 'error' key in the response
        response.raise_for_status()

        return response.json()

