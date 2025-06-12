"""Tests for RTLS generator."""

import pytest
import math
from datetime import datetime

from src.rtls_generator import RTLSGenerator
from src.models import Position, Tag, Zone


@pytest.fixture
def config():
    """Test configuration."""
    return {
        'rtls': {
            'update_interval': 1.0,
            'movement': {
                'max_speed': 5.0,
                'acceleration': 0.5,
                'turn_rate': 45.0
            },
            'zones': [
                {
                    'id': 'zone_1',
                    'name': 'Zone 1',
                    'bounds': {
                        'x_min': 0,
                        'x_max': 50,
                        'y_min': 0,
                        'y_max': 50,
                        'z_min': 0,
                        'z_max': 5
                    }
                }
            ],
            'tags': [
                {
                    'id': 'tag_001',
                    'name': 'Test Tag',
                    'type': 'person',
                    'initial_position': {'x': 25, 'y': 25, 'z': 0},
                    'battery': 100
                }
            ]
        }
    }


@pytest.fixture
def rtls_generator(config):
    """Create RTLS generator instance."""
    return RTLSGenerator(config)


def test_rtls_generator_init(rtls_generator):
    """Test RTLS generator initialization."""
    assert len(rtls_generator.zones) == 1
    assert len(rtls_generator.tags) == 1
    assert 'tag_001' in rtls_generator.tags


def test_zone_contains():
    """Test zone boundary checking."""
    zone = Zone(
        id='test_zone',
        name='Test Zone',
        x_min=0, x_max=10,
        y_min=0, y_max=10,
        z_min=0, z_max=5
    )
    
    # Inside zone
    assert zone.contains(Position(5, 5, 2)) is True
    
    # On boundary
    assert zone.contains(Position(0, 0, 0)) is True
    assert zone.contains(Position(10, 10, 5)) is True
    
    # Outside zone
    assert zone.contains(Position(-1, 5, 2)) is False
    assert zone.contains(Position(5, 11, 2)) is False
    assert zone.contains(Position(5, 5, 6)) is False


def test_position_distance():
    """Test distance calculation between positions."""
    pos1 = Position(0, 0, 0)
    pos2 = Position(3, 4, 0)
    
    distance = pos1.distance_to(pos2)
    assert distance == 5.0  # 3-4-5 triangle
    
    # 3D distance
    pos3 = Position(0, 0, 5)
    distance = pos1.distance_to(pos3)
    assert distance == 5.0


def test_get_current_zone(rtls_generator):
    """Test zone detection for position."""
    # Position inside zone
    zone_id = rtls_generator._get_current_zone(Position(25, 25, 0))
    assert zone_id == 'zone_1'
    
    # Position outside any zone
    zone_id = rtls_generator._get_current_zone(Position(100, 100, 0))
    assert zone_id is None


def test_update_tag_position(rtls_generator):
    """Test tag position update."""
    tag = rtls_generator.tags['tag_001']
    initial_position = Position(tag.position.x, tag.position.y, tag.position.z)
    
    # Update position
    alert = rtls_generator.update_tag_position(tag, 1.0)
    
    # Check that position changed (or stayed same if speed was 0)
    assert tag.last_update is not None
    
    # Battery should be same or slightly decreased
    assert tag.battery <= 100
    
    # RSSI should be in valid range
    assert -90 <= tag.rssi <= -40


def test_zone_transition(rtls_generator):
    """Test zone transition detection."""
    tag = rtls_generator.tags['tag_001']
    
    # Move tag outside zone
    tag.position.x = 100
    tag.position.y = 100
    
    alert = rtls_generator.update_tag_position(tag, 0.1)
    
    # Should generate exit alert
    assert tag.zone_id is None


def test_get_location_update(rtls_generator):
    """Test location update generation."""
    location = rtls_generator.get_location_update('tag_001')
    
    assert location is not None
    assert location.tag_id == 'tag_001'
    assert 'x' in location.location
    assert 'y' in location.location
    assert 'z' in location.location
    
    # Non-existent tag
    location = rtls_generator.get_location_update('invalid_tag')
    assert location is None


def test_get_tags_in_zone(rtls_generator):
    """Test getting tags in a specific zone."""
    tags = rtls_generator.get_tags_in_zone('zone_1')
    assert len(tags) == 1
    assert tags[0].id == 'tag_001'
    
    # Empty zone
    tags = rtls_generator.get_tags_in_zone('non_existent_zone')
    assert len(tags) == 0


def test_simulate_anomaly(rtls_generator):
    """Test anomaly simulation."""
    tag = rtls_generator.tags['tag_001']
    
    # Low battery
    rtls_generator.simulate_anomaly('tag_001', 'low_battery')
    assert tag.battery < 20
    
    # Weak signal
    original_rssi = tag.rssi
    rtls_generator.simulate_anomaly('tag_001', 'weak_signal')
    assert tag.rssi <= -80
    
    # Fast movement
    rtls_generator.simulate_anomaly('tag_001', 'fast_movement')
    assert tag.speed > rtls_generator.movement_config['max_speed']
    
    # Out of bounds
    rtls_generator.simulate_anomaly('tag_001', 'out_of_bounds')
    assert tag.position.x < 0 or tag.position.y < 0


def test_movement_physics(rtls_generator):
    """Test realistic movement physics."""
    tag = rtls_generator.tags['tag_001']
    tag.speed = 2.0
    tag.heading = 0  # Moving east
    
    initial_x = tag.position.x
    
    # Move for 1 second
    rtls_generator._move_tag(tag, 1.0, max_speed=5.0)
    
    # Should have moved approximately 2 meters east (with some randomness)
    assert tag.position.x > initial_x
    
    # Speed should be within bounds
    assert 0 <= tag.speed <= 5.0