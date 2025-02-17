# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2021 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Implementation of REST api client."""

from typing import List, Optional
from urllib.parse import urlencode

import requests
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message


class RestClient:
    """REST api client."""

    def __init__(self, rest_address: str):
        """
        Create REST api client

        :param rest_address: Address of REST node
        """
        self._session = requests.session()
        self.rest_address = rest_address

    def get(
        self,
        url_base_path: str,
        request: Optional[Message] = None,
        used_params: Optional[List[str]] = None,
    ) -> bytes:
        """
        Send a GET request

        :param url_base_path: URL base path
        :param request: Protobuf coded request
        :param used_params: Parameters to be removed from request after converting it to dict

        :raises RuntimeError: if response code is not 200

        :return: Content of response
        """
        if request is None:
            url = f"{self.rest_address}{url_base_path}"
        else:
            json_request = MessageToDict(request)

            # Remove params that are already in url_base_path
            if used_params is not None:
                for param in used_params:
                    json_request.pop(param)

            url_encoded_request = urlencode(json_request, doseq=True)

            if len(url_encoded_request) == 0:
                url = f"{self.rest_address}{url_base_path}"
            else:
                url = f"{self.rest_address}{url_base_path}?{url_encoded_request}"

        response = self._session.get(url=url)
        if response.status_code != 200:
            raise RuntimeError(
                f"Error when sending a GET request.\n Response: {response.status_code}, {str(response.content)})"
            )
        return response.content

    def post(self, url_base_path: str, request: Message) -> bytes:
        """
        Send a POST request

        :param url_base_path: URL base path
        :param request: Protobuf coded request

        :raises RuntimeError: if response code is not 200

        :return: Content of response
        """
        json_request = MessageToDict(request)

        headers = {"Content-type": "application/json", "Accept": "application/json"}
        response = self._session.post(
            url=f"{self.rest_address}{url_base_path}",
            json=json_request,
            headers=headers,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Error when sending a POST request.\n Request: {json_request}\n Response: {response.status_code}, {str(response.content)})"
            )
        return response.content

    def __del__(self):
        self._session.close()
