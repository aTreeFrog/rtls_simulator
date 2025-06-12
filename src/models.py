"""Data models for RTLS system."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class Position:
    """3D position coordinates."""
    x: float
    y: float
    z: float = 0.0
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate Euclidean distance to another position."""
        return ((self.x - other.x) ** 2 + 
                (self.y - other.y) ** 2 + 
                (self.z - other.z) ** 2) ** 0.5


@dataclass
class Zone:
    """Zone definition with boundaries."""
    id: str
    name: str
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float
    
    def contains(self, position: Position) -> bool:
        """Check if a position is within this zone."""
        return (self.x_min <= position.x <= self.x_max and
                self.y_min <= position.y <= self.y_max and
                self.z_min <= position.z <= self.z_max)


@dataclass
class Tag:
    """RTLS tag information."""
    id: str
    name: str
    type: str
    position: Position
    speed: float = 0.0
    heading: float = 0.0
    battery: int = 100
    rssi: int = -70
    last_update: Optional[datetime] = None
    zone_id: Optional[str] = None


@dataclass
class LocationUpdate:
    """Location update message."""
    tag_id: str
    timestamp: str
    location: Dict[str, float]
    zone_id: Optional[str]
    speed: float
    heading: float
    battery: int
    rssi: int
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_tag(cls, tag: Tag) -> 'LocationUpdate':
        """Create from Tag object."""
        return cls(
            tag_id=tag.id,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            location={
                'x': round(tag.position.x, 2),
                'y': round(tag.position.y, 2),
                'z': round(tag.position.z, 2)
            },
            zone_id=tag.zone_id,
            speed=round(tag.speed, 2),
            heading=round(tag.heading, 1),
            battery=tag.battery,
            rssi=tag.rssi
        )


@dataclass
class ZoneAlert:
    """Zone transition alert."""
    tag_id: str
    tag_name: str
    timestamp: str
    event_type: str  # 'entered' or 'exited'
    zone_id: str
    zone_name: str
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self))


@dataclass
class SystemStatus:
    """System status message."""
    timestamp: str
    active_tags: int
    update_rate: float
    broker_connected: bool
    message: str
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self))