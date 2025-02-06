# -*- coding: utf-8 -*-
from typing import Any

import requests


class CompletionExecutor:
    def __init__(self, host: str, api_key: str, request_id: str) -> None:
        self._host = host
        self._api_key = api_key
        self._request_id = request_id

    def execute(self, completion_request: dict[str, Any]) -> str:
        headers = {
            "Authorization": self._api_key,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self._request_id,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
        }
        chat_response = ""
        with requests.post(
            self._host + "/testapp/v1/chat-completions/HCX-003", headers=headers, json=completion_request, stream=True
        ) as r:
            for line in r.iter_lines():
                if line:
                    chat_response + line.decode("utf-8")
        return chat_response
