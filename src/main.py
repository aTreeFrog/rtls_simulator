"""Main entry point for MQTT RTLS mock data publisher."""

import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
import yaml

from .mqtt_client import MQTTClient
from .rtls_generator import RTLSGenerator
from .models import SystemStatus


class RTLSPublisher:
    """Main RTLS data publisher application."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.running = False
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        self.mqtt_client = MQTTClient(self.config)
        self.rtls_generator = RTLSGenerator(self.config)
        self.update_interval = self.config['rtls']['update_interval']
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self):
        """Set up logging configuration."""
        log_config = self.config.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger = logging.getLogger(__name__)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self):
        """Start the RTLS publisher."""
        self.logger.info("Starting MQTT RTLS Publisher...")
        
        # Connect to MQTT broker
        if not self.mqtt_client.connect():
            self.logger.error("Failed to connect to MQTT broker")
            return
        
        # Publish initial status
        status = SystemStatus(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            active_tags=len(self.rtls_generator.get_all_tags()),
            update_rate=self.update_interval,
            broker_connected=True,
            message="System started"
        )
        self.mqtt_client.publish_status(status)
        
        self.running = True
        self.logger.info("RTLS Publisher started successfully")
        
        # Main loop
        try:
            while self.running:
                start_time = time.time()
                
                # Update all tags
                for tag in self.rtls_generator.get_all_tags():
                    # Update position
                    alert = self.rtls_generator.update_tag_position(tag, self.update_interval)
                    
                    # Publish location update
                    location = self.rtls_generator.get_location_update(tag.id)
                    if location:
                        self.mqtt_client.publish_location(location)
                    
                    # Publish zone alert if transition occurred
                    if alert:
                        self.mqtt_client.publish_alert(alert)
                        self.logger.info(f"Zone transition: {alert.tag_name} {alert.event_type} {alert.zone_name}")
                
                # Update zone occupancy
                for zone in self.rtls_generator.zones:
                    tags_in_zone = self.rtls_generator.get_tags_in_zone(zone.id)
                    self.mqtt_client.publish_zone_tags(zone.id, tags_in_zone)
                
                # Calculate sleep time to maintain update rate
                elapsed = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Stop the RTLS publisher."""
        self.running = False
        
        # Publish shutdown status
        status = SystemStatus(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            active_tags=0,
            update_rate=0,
            broker_connected=False,
            message="System shutting down"
        )
        self.mqtt_client.publish_status(status)
        
        # Disconnect from broker
        self.mqtt_client.disconnect()
        self.logger.info("RTLS Publisher stopped")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MQTT RTLS Mock Data Publisher")
    parser.add_argument(
        '-c', '--config',
        default='config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Override log level if verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and start publisher
    publisher = RTLSPublisher(args.config)
    publisher.start()


if __name__ == '__main__':
    main()