import logging
from http import HTTPMethod

import requests

from vaultapp.api.region import HarveyRegion

logger = logging.getLogger(__name__)


class HarveyRequest:
    def __init__(self, auth_key: str, region: HarveyRegion = HarveyRegion.NA):
        self.region = region
        self.auth_key = auth_key

    def exec(self, endpoint: str, method: HTTPMethod, data=None, files=None):
        headers = {
            'Authorization': f'Bearer {self.auth_key}'
        }

        url = f"{self.region}{endpoint}"

        response = requests.request(method, url, headers=headers, data=data, files=files)

        response.raise_for_status()

        return response.json()
