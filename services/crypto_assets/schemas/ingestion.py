from pydantic import BaseModel, ConfigDict

from services.crypto_assets.models import IngestionStatus, IngestionTriggerType


class IngestionRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    connector_type: str
    trigger_type: IngestionTriggerType
    status: IngestionStatus
    stats_json: dict | None = None
