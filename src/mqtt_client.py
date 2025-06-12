"""MQTT client for publishing RTLS data."""

import json
import logging
from typing import Dict, List, Optional
import paho.mqtt.client as mqtt

from .models import LocationUpdate, ZoneAlert, SystemStatus, Tag


class MQTTClient:
    """MQTT client for RTLS data publishing."""
    
    def __init__(self, config: Dict):
        self.config = config['mqtt']
        self.client = mqtt.Client(client_id=self.config['client_id'])
        self.logger = logging.getLogger(__name__)
        self.connected = False
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        # Set credentials if provided
        if self.config.get('username') and self.config.get('password'):
            self.client.username_pw_set(
                self.config['username'],
                self.config['password']
            )
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when client connects to broker."""
        if rc == 0:
            self.connected = True
            self.logger.info(f"Connected to MQTT broker at {self.config['broker']}:{self.config['port']}")
        else:
            self.logger.error(f"Failed to connect, return code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when client disconnects from broker."""
        self.connected = False
        if rc != 0:
            self.logger.warning(f"Unexpected disconnection, return code {rc}")
    
    def _on_publish(self, client, userdata, mid):
        """Callback for when a message is published."""
        self.logger.debug(f"Message {mid} published")
    
    def connect(self) -> bool:
        """Connect to MQTT broker."""
        try:
            self.client.connect(
                self.config['broker'],
                self.config['port'],
                self.config.get('keepalive', 60)
            )
            self.client.loop_start()
            
            # Wait for connection
            import time
            timeout = 5
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
            
            return self.connected
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
    
    def publish_location(self, location: LocationUpdate) -> bool:
        """Publish location update."""
        topic = f"rtls/location/{location.tag_id}"
        payload = location.to_json()
        
        result = self.client.publish(
            topic,
            payload,
            qos=self.config.get('qos', 1),
            retain=True
        )
        
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    
    def publish_zone_tags(self, zone_id: str, tags: List[Tag]) -> bool:
        """Publish list of tags in a zone."""
        topic = f"rtls/zone/{zone_id}/tags"
        
        tag_list = [
            {
                'tag_id': tag.id,
                'name': tag.name,
                'type': tag.type,
                'entered_at': tag.last_update.isoformat() if tag.last_update else None
            }
            for tag in tags
        ]
        
        payload = json.dumps({
            'zone_id': zone_id,
            'tag_count': len(tags),
            'tags': tag_list
        })
        
        result = self.client.publish(
            topic,
            payload,
            qos=self.config.get('qos', 1),
            retain=True
        )
        
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    
    def publish_alert(self, alert: ZoneAlert) -> bool:
        """Publish zone transition alert."""
        topic = "rtls/alerts"
        payload = alert.to_json()
        
        result = self.client.publish(
            topic,
            payload,
            qos=self.config.get('qos', 1),
            retain=False
        )
        
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    
    def publish_status(self, status: SystemStatus) -> bool:
        """Publish system status."""
        topic = "rtls/status"
        payload = status.to_json()
        
        result = self.client.publish(
            topic,
            payload,
            qos=self.config.get('qos', 1),
            retain=True
        )
        
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    
    def clear_retained_messages(self):
        """Clear all retained messages by publishing empty payloads."""
        topics = [
            "rtls/status",
            "rtls/location/+",
            "rtls/zone/+/tags"
        ]
        
        for topic in topics:
            self.client.publish(topic, "", qos=1, retain=True)