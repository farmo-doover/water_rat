import json
from typing import Any


class Message:
    def __init__(self, client, data, channel_id):
        self.client = client
        self.channel_id = channel_id
        self._payload = None

        self._from_data(data)

    def __repr__(self):
        if self._payload is not None:
            return f"<Message message_id={self.id}, payload={self._payload}>"
        return f"<Message message_id={self.id}>"

    def _from_data(self, data: dict[str, Any]):
        # {'agent': '9fb5d629-ce7f-4b08-b17a-c267cbcd0427', 'message': 'a7b493dd-4577-4f81-ac3d-f1b3be680b12', 'type': 'base', 'timestamp': 1715646840.250541}
        self.id = data["message"]
        self.agent_id = data["agent"]
        self.timestamp = data["timestamp"]

        if not self.channel_id:
            self.channel_id = data.get("channel")

        self._payload = data.get("payload")

    def update(self):
        data = self.client._get_message_raw(self.channel_id, self.id)
        self._from_data(data)

    def fetch_payload(self):
        if self._payload is not None:
            return self._payload

        data = self.client._get_message_raw(self.channel_id, self.id)
        self._payload = json.loads(data["payload"])
        return self._payload
