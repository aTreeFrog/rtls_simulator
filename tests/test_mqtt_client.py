"""Tests for MQTT client."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.mqtt_client import MQTTClient
from src.models import LocationUpdate, ZoneAlert, SystemStatus, Tag, Position


@pytest.fixture
def config():
    """Test configuration."""
    return {
        'mqtt': {
            'broker': 'localhost',
            'port': 1883,
            'client_id': 'test_client',
            'qos': 1,
            'keepalive': 60
        }
    }


@pytest.fixture
def mqtt_client(config):
    """Create MQTT client instance."""
    return MQTTClient(config)


def test_mqtt_client_init(mqtt_client, config):
    """Test MQTT client initialization."""
    assert mqtt_client.config == config['mqtt']
    assert mqtt_client.connected is False
    assert mqtt_client.client is not None


@patch('paho.mqtt.client.Client')
def test_connect_success(mock_mqtt_class, mqtt_client):
    """Test successful connection to broker."""
    mock_client = Mock()
    mock_mqtt_class.return_value = mock_client
    
    # Create new client with mocked mqtt
    client = MQTTClient({'mqtt': mqtt_client.config})
    client.connected = True  # Simulate successful connection
    
    result = client.connect()
    
    assert result is True


def test_publish_location(mqtt_client):
    """Test publishing location update."""
    # Create mock MQTT client
    mqtt_client.client = Mock()
    mqtt_client.client.publish.return_value = Mock(rc=0)
    
    # Create location update
    location = LocationUpdate(
        tag_id='tag_001',
        timestamp=datetime.utcnow().isoformat() + 'Z',
        location={'x': 10.5, 'y': 20.3, 'z': 0.0},
        zone_id='zone_1',
        speed=2.5,
        heading=45.0,
        battery=90,
        rssi=-60
    )
    
    result = mqtt_client.publish_location(location)
    
    assert result is True
    mqtt_client.client.publish.assert_called_once()
    
    # Check publish arguments
    call_args = mqtt_client.client.publish.call_args
    assert call_args[0][0] == 'rtls/location/tag_001'
    assert json.loads(call_args[0][1])['tag_id'] == 'tag_001'


def test_publish_alert(mqtt_client):
    """Test publishing zone alert."""
    mqtt_client.client = Mock()
    mqtt_client.client.publish.return_value = Mock(rc=0)
    
    alert = ZoneAlert(
        tag_id='tag_001',
        tag_name='Test Tag',
        timestamp=datetime.utcnow().isoformat() + 'Z',
        event_type='entered',
        zone_id='zone_1',
        zone_name='Zone 1'
    )
    
    result = mqtt_client.publish_alert(alert)
    
    assert result is True
    mqtt_client.client.publish.assert_called_once_with(
        'rtls/alerts',
        alert.to_json(),
        qos=1,
        retain=False
    )


def test_publish_zone_tags(mqtt_client):
    """Test publishing zone occupancy."""
    mqtt_client.client = Mock()
    mqtt_client.client.publish.return_value = Mock(rc=0)
    
    tags = [
        Tag(
            id='tag_001',
            name='Tag 1',
            type='person',
            position=Position(10, 20),
            zone_id='zone_1',
            last_update=datetime.utcnow()
        ),
        Tag(
            id='tag_002',
            name='Tag 2',
            type='vehicle',
            position=Position(15, 25),
            zone_id='zone_1',
            last_update=datetime.utcnow()
        )
    ]
    
    result = mqtt_client.publish_zone_tags('zone_1', tags)
    
    assert result is True
    
    # Check published data
    call_args = mqtt_client.client.publish.call_args
    assert call_args[0][0] == 'rtls/zone/zone_1/tags'
    
    payload = json.loads(call_args[0][1])
    assert payload['zone_id'] == 'zone_1'
    assert payload['tag_count'] == 2
    assert len(payload['tags']) == 2


def test_publish_status(mqtt_client):
    """Test publishing system status."""
    mqtt_client.client = Mock()
    mqtt_client.client.publish.return_value = Mock(rc=0)
    
    status = SystemStatus(
        timestamp=datetime.utcnow().isoformat() + 'Z',
        active_tags=5,
        update_rate=1.0,
        broker_connected=True,
        message='System running'
    )
    
    result = mqtt_client.publish_status(status)
    
    assert result is True
    mqtt_client.client.publish.assert_called_once_with(
        'rtls/status',
        status.to_json(),
        qos=1,
        retain=True
    )


def test_disconnect(mqtt_client):
    """Test disconnection from broker."""
    mqtt_client.client = Mock()
    mqtt_client.connected = True
    
    mqtt_client.disconnect()
    
    mqtt_client.client.loop_stop.assert_called_once()
    mqtt_client.client.disconnect.assert_called_once()
    assert mqtt_client.connected is False