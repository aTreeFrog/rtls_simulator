"""Example of using the RTLS publisher programmatically."""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mqtt_client import MQTTClient
from src.rtls_generator import RTLSGenerator
from src.models import SystemStatus
import yaml


def custom_publisher_example():
    """Example of creating a custom publisher."""
    
    # Load configuration
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create components
    mqtt_client = MQTTClient(config)
    rtls_generator = RTLSGenerator(config)
    
    print("Custom RTLS Publisher Example")
    print("=" * 60)
    
    # Connect to broker
    if not mqtt_client.connect():
        print("Failed to connect to MQTT broker")
        return
    
    print("Connected to MQTT broker")
    
    try:
        # Run for 30 seconds
        duration = 30
        interval = 0.5  # Faster update rate
        
        print(f"Publishing data for {duration} seconds...")
        print("Watch the subscriber to see the data!")
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Update a specific tag
            tag = rtls_generator.tags.get('tag_001')
            if tag:
                # Force movement
                tag.speed = 3.0
                alert = rtls_generator.update_tag_position(tag, interval)
                
                # Get and publish location
                location = rtls_generator.get_location_update(tag.id)
                if location:
                    mqtt_client.publish_location(location)
                    print(f"Published location for {tag.name}: "
                          f"({location.location['x']:.1f}, {location.location['y']:.1f})")
                
                # Publish alert if zone changed
                if alert:
                    mqtt_client.publish_alert(alert)
                    print(f"Zone transition: {alert.tag_name} {alert.event_type} {alert.zone_name}")
            
            time.sleep(interval)
        
        # Simulate anomalies
        print("\nSimulating anomalies...")
        
        # Low battery
        rtls_generator.simulate_anomaly('tag_002', 'low_battery')
        location = rtls_generator.get_location_update('tag_002')
        if location:
            mqtt_client.publish_location(location)
            print(f"Simulated low battery for tag_002: {location.battery}%")
        
        # Weak signal
        rtls_generator.simulate_anomaly('tag_003', 'weak_signal')
        location = rtls_generator.get_location_update('tag_003')
        if location:
            mqtt_client.publish_location(location)
            print(f"Simulated weak signal for tag_003: {location.rssi} dBm")
        
        time.sleep(2)
        
    finally:
        # Clean up
        print("\nShutting down...")
        mqtt_client.disconnect()
        print("Done!")


def batch_update_example():
    """Example of batch updating multiple tags."""
    
    # Load configuration
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create components
    mqtt_client = MQTTClient(config)
    rtls_generator = RTLSGenerator(config)
    
    print("\nBatch Update Example")
    print("=" * 60)
    
    # Connect to broker
    if not mqtt_client.connect():
        print("Failed to connect to MQTT broker")
        return
    
    try:
        # Update all tags 10 times
        for i in range(10):
            print(f"\nBatch update {i+1}/10")
            
            # Update all tags
            for tag in rtls_generator.get_all_tags():
                alert = rtls_generator.update_tag_position(tag, 1.0)
                location = rtls_generator.get_location_update(tag.id)
                
                if location:
                    mqtt_client.publish_location(location)
                
                if alert:
                    mqtt_client.publish_alert(alert)
                    print(f"  Zone transition: {alert.tag_name} {alert.event_type} {alert.zone_name}")
            
            # Update zone occupancy
            for zone in rtls_generator.zones:
                tags_in_zone = rtls_generator.get_tags_in_zone(zone.id)
                mqtt_client.publish_zone_tags(zone.id, tags_in_zone)
                if tags_in_zone:
                    print(f"  Zone {zone.name}: {len(tags_in_zone)} tags")
            
            time.sleep(1)
        
    finally:
        mqtt_client.disconnect()
        print("\nBatch update complete!")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="RTLS Publisher Examples")
    parser.add_argument(
        'example',
        choices=['custom', 'batch'],
        help='Which example to run'
    )
    
    args = parser.parse_args()
    
    if args.example == 'custom':
        custom_publisher_example()
    else:
        batch_update_example()