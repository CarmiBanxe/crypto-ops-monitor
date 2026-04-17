import enum


class WalletSourceType(str, enum.Enum):
    AILINK = "AILINK"
    MANUAL = "MANUAL"
    EXCHANGE = "EXCHANGE"
    STAKING = "STAKING"


class WalletType(str, enum.Enum):
    CUSTODY = "CUSTODY"
    NON_CUSTODY = "NON_CUSTODY"
    EXCHANGE = "EXCHANGE"
    STAKING = "STAKING"
    UNKNOWN = "UNKNOWN"


class RecordStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISABLED = "DISABLED"


class CounterpartyKind(str, enum.Enum):
    CORPORATE = "CORPORATE"
    INDIVIDUAL = "INDIVIDUAL"
    UNKNOWN = "UNKNOWN"


class IngestionTriggerType(str, enum.Enum):
    MANUAL = "MANUAL"
    SCHEDULED = "SCHEDULED"
    WEBHOOK = "WEBHOOK"


class IngestionStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class Direction(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"
    UNKNOWN = "UNKNOWN"
