import json
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any

@dataclass
class Check:
    component: str
    status: str
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert a Check instance to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Check':
        """Create a Check instance from a dictionary."""
        return cls(
            component=data.get("component", ""),
            status=data.get("status", ""),
            error=data.get("error", "")
        )

@dataclass
class BootCheckModel:
    checks: List[Check] = field(default_factory=list)
    overall_status: str = ""
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert a BootCheckModel instance to a dictionary."""
        return {
            "checks": [check.to_dict() for check in self.checks],
            "overall_status": self.overall_status,
            "message": self.message
        }

    def to_json(self) -> str:
        """Serialize the BootCheckModel to a JSON string."""
        return json.dumps(self.to_dict(), separators=(',', ':'))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BootCheckModel':
        """Create a BootCheckModel instance from a dictionary."""
        checks_list = data.get("checks", [])
        components = [Check.from_dict(item) for item in checks_list]
        return cls(
            checks=components,
            overall_status=data.get("overall_status", ""),
            message=data.get("message", "")
        )

    @classmethod
    def from_json(cls, json_string: str) -> 'BootCheckModel':
        """Deserialize a JSON string to a BootCheckModel instance."""
        data = json.loads(json_string)
        return cls.from_dict(data)

