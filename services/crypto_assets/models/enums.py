import enum


class WalletSourceType(enum.StrEnum):
    AILINK = "AILINK"
    MANUAL = "MANUAL"
    EXCHANGE = "EXCHANGE"
    STAKING = "STAKING"


class WalletType(enum.StrEnum):
    CUSTODY = "CUSTODY"
    NON_CUSTODY = "NON_CUSTODY"
    EXCHANGE = "EXCHANGE"
    STAKING = "STAKING"
    UNKNOWN = "UNKNOWN"


class RecordStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISABLED = "DISABLED"


class CounterpartyKind(enum.StrEnum):
    CORPORATE = "CORPORATE"
    INDIVIDUAL = "INDIVIDUAL"
    UNKNOWN = "UNKNOWN"


class IngestionTriggerType(enum.StrEnum):
    MANUAL = "MANUAL"
    SCHEDULED = "SCHEDULED"
    WEBHOOK = "WEBHOOK"


class IngestionStatus(enum.StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class Direction(enum.StrEnum):
    IN = "IN"
    OUT = "OUT"
    UNKNOWN = "UNKNOWN"
