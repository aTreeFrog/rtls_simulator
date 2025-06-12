"""RTLS data generator for mock location updates."""

import random
import math
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import numpy as np

from .models import Tag, Position, Zone, LocationUpdate, ZoneAlert


class RTLSGenerator:
    """Generate realistic RTLS movement data."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.zones = self._init_zones()
        self.tags = self._init_tags()
        self.movement_config = config['rtls']['movement']
        
    def _init_zones(self) -> List[Zone]:
        """Initialize zones from configuration."""
        zones = []
        for zone_config in self.config['rtls']['zones']:
            zone = Zone(
                id=zone_config['id'],
                name=zone_config['name'],
                x_min=zone_config['bounds']['x_min'],
                x_max=zone_config['bounds']['x_max'],
                y_min=zone_config['bounds']['y_min'],
                y_max=zone_config['bounds']['y_max'],
                z_min=zone_config['bounds']['z_min'],
                z_max=zone_config['bounds']['z_max']
            )
            zones.append(zone)
        return zones
    
    def _init_tags(self) -> Dict[str, Tag]:
        """Initialize tags from configuration."""
        tags = {}
        for tag_config in self.config['rtls']['tags']:
            position = Position(
                x=tag_config['initial_position']['x'],
                y=tag_config['initial_position']['y'],
                z=tag_config['initial_position'].get('z', 0)
            )
            
            tag = Tag(
                id=tag_config['id'],
                name=tag_config['name'],
                type=tag_config['type'],
                position=position,
                battery=tag_config.get('battery', 100),
                heading=random.uniform(0, 360)
            )
            
            # Set initial zone
            tag.zone_id = self._get_current_zone(position)
            tags[tag_config['id']] = tag
            
        return tags
    
    def _get_current_zone(self, position: Position) -> Optional[str]:
        """Get the zone ID containing the position."""
        for zone in self.zones:
            if zone.contains(position):
                return zone.id
        return None
    
    def _get_zone_by_id(self, zone_id: str) -> Optional[Zone]:
        """Get zone object by ID."""
        for zone in self.zones:
            if zone.id == zone_id:
                return zone
        return None
    
    def update_tag_position(self, tag: Tag, dt: float) -> Optional[ZoneAlert]:
        """Update tag position with realistic movement."""
        # Update battery (slow drain)
        if random.random() < 0.001:
            tag.battery = max(0, tag.battery - 1)
        
        # Update RSSI with some noise
        tag.rssi = max(-90, min(-40, tag.rssi + random.randint(-5, 5)))
        
        # Movement logic based on tag type
        if tag.type == 'asset':
            # Assets move rarely
            if random.random() < 0.01:
                self._move_tag(tag, dt, max_speed=1.0)
        elif tag.type == 'vehicle':
            # Vehicles move frequently at higher speeds
            self._move_tag(tag, dt, max_speed=self.movement_config['max_speed'])
        else:  # person
            # People move at moderate speeds
            self._move_tag(tag, dt, max_speed=2.0)
        
        # Check for zone transitions
        new_zone_id = self._get_current_zone(tag.position)
        alert = None
        
        if new_zone_id != tag.zone_id:
            # Zone transition occurred
            if tag.zone_id is not None:
                # Exited previous zone
                old_zone = self._get_zone_by_id(tag.zone_id)
                if old_zone:
                    alert = ZoneAlert(
                        tag_id=tag.id,
                        tag_name=tag.name,
                        timestamp=datetime.utcnow().isoformat() + 'Z',
                        event_type='exited',
                        zone_id=old_zone.id,
                        zone_name=old_zone.name
                    )
            
            if new_zone_id is not None:
                # Entered new zone
                new_zone = self._get_zone_by_id(new_zone_id)
                if new_zone:
                    alert = ZoneAlert(
                        tag_id=tag.id,
                        tag_name=tag.name,
                        timestamp=datetime.utcnow().isoformat() + 'Z',
                        event_type='entered',
                        zone_id=new_zone.id,
                        zone_name=new_zone.name
                    )
            
            tag.zone_id = new_zone_id
        
        tag.last_update = datetime.utcnow()
        return alert
    
    def _move_tag(self, tag: Tag, dt: float, max_speed: float):
        """Move tag with realistic physics."""
        # Random walk with momentum
        turn_rate = self.movement_config['turn_rate']
        acceleration = self.movement_config['acceleration']
        
        # Update heading
        heading_change = random.uniform(-turn_rate, turn_rate) * dt
        tag.heading = (tag.heading + heading_change) % 360
        
        # Update speed
        speed_change = random.uniform(-acceleration, acceleration) * dt
        tag.speed = max(0, min(max_speed, tag.speed + speed_change))
        
        # Calculate new position
        heading_rad = math.radians(tag.heading)
        dx = tag.speed * math.cos(heading_rad) * dt
        dy = tag.speed * math.sin(heading_rad) * dt
        
        new_x = tag.position.x + dx
        new_y = tag.position.y + dy
        
        # Boundary checking - bounce off walls
        for zone in self.zones:
            if zone.contains(tag.position):
                if new_x <= zone.x_min or new_x >= zone.x_max:
                    tag.heading = (180 - tag.heading) % 360
                    new_x = max(zone.x_min, min(zone.x_max, new_x))
                
                if new_y <= zone.y_min or new_y >= zone.y_max:
                    tag.heading = (-tag.heading) % 360
                    new_y = max(zone.y_min, min(zone.y_max, new_y))
                
                break
        
        tag.position.x = new_x
        tag.position.y = new_y
        
        # Add slight vertical movement for people
        if tag.type == 'person' and random.random() < 0.1:
            tag.position.z += random.uniform(-0.1, 0.1)
            tag.position.z = max(0, min(2, tag.position.z))
    
    def get_location_update(self, tag_id: str) -> Optional[LocationUpdate]:
        """Get current location update for a tag."""
        tag = self.tags.get(tag_id)
        if not tag:
            return None
        
        return LocationUpdate.from_tag(tag)
    
    def get_all_tags(self) -> List[Tag]:
        """Get all tags."""
        return list(self.tags.values())
    
    def get_tags_in_zone(self, zone_id: str) -> List[Tag]:
        """Get all tags currently in a zone."""
        return [tag for tag in self.tags.values() if tag.zone_id == zone_id]
    
    def simulate_anomaly(self, tag_id: str, anomaly_type: str):
        """Simulate various anomalies for testing."""
        tag = self.tags.get(tag_id)
        if not tag:
            return
        
        if anomaly_type == 'low_battery':
            tag.battery = random.randint(5, 15)
        elif anomaly_type == 'weak_signal':
            tag.rssi = random.randint(-85, -80)
        elif anomaly_type == 'fast_movement':
            tag.speed = self.movement_config['max_speed'] * 2
        elif anomaly_type == 'out_of_bounds':
            tag.position.x = -10
            tag.position.y = -10