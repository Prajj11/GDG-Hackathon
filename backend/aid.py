"""Partner boundary. The demo adapter performs NO network calls or human dispatch."""
from typing import Literal, Protocol
from pydantic import BaseModel

class AidPayload(BaseModel):
    schema_version: Literal['1'] = '1'
    report_id: str
    selected_context: str
    report_text: str
    urgency_level: str
    detection_context: dict | None = None
    # No guardian identifier, anonymous receipt token, or original chat log.

class AidReceipt(BaseModel):
    channel_name: str
    status: Literal['simulated_received']

class AidProvider(Protocol):
    def route(self, payload: AidPayload, *, idempotency_key: str) -> AidReceipt: ...

class SimulatedAidProvider:
    def route(self, payload: AidPayload, *, idempotency_key: str) -> AidReceipt:
        return AidReceipt(channel_name='Simulated Child Helpline Endpoint', status='simulated_received')

aid_provider: AidProvider = SimulatedAidProvider()
