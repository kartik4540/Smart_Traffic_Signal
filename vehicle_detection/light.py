import torch
import cv2
import numpy as np
from PIL import Image
import time
import os
from typing import Dict, Tuple, Optional
import logging
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TrafficConfig:
    """Configuration for traffic light system"""
    confidence_threshold: float = 0.4
    min_green_time: int = 10
    max_green_time: int = 30
    cars_per_second: int = 5
    yellow_time: int = 3
    max_cycles: int = 5
    window_size: Tuple[int, int] = (800, 600)
    car_classes: list = ('car', 'truck', 'bus', 'motorcycle')

class TrafficLightSystem:
    def __init__(self, config: TrafficConfig = TrafficConfig()):
        """Initialize the traffic light system"""
        self.config = config
        try:
            self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)
            logger.info("YOLOv5 model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLOv5 model: {e}")
            raise

    def count_cars(self, image_path: str) -> Tuple[int, Optional[torch.Tensor]]:
        """Detect cars in an image and return the count."""
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image not found: {image_path}")
                return 0, None

            # Load and process image
            img = Image.open(image_path)
            results = self.model(img)
            
            # Get detections as pandas DataFrame
            detections = results.pandas().xyxy[0]
            
            # Filter for vehicle classes and confidence threshold
            vehicles = detections[
                (detections['name'].isin(self.config.car_classes)) & 
                (detections['confidence'] >= self.config.confidence_threshold)
            ]

            return len(vehicles), results

        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return 0, None

    def calculate_timer(self, car_count: int) -> int:
        """Calculate green light timer based on car count."""
        return min(
            max(self.config.min_green_time, car_count * self.config.cars_per_second),
            self.config.max_green_time
        )

    def draw_traffic_ui(self, active: str, next_adjacent: str, timers: Dict[str, int],
                       green_remaining: int, red_remaining: int) -> None:
        """Display enhanced traffic light status using OpenCV."""
        # Create a blank image with better resolution
        img = np.zeros((self.config.window_size[1], self.config.window_size[0], 3), dtype=np.uint8)
        
        # Add background color
        img[:] = (40, 40, 40)

        # Define positions for signals with better spacing
        positions = {
            'North': (400, 150),
            'East': (600, 300),
            'South': (400, 450),
            'West': (200, 300),
        }

        # Draw traffic signals with enhanced visuals
        for direction, pos in positions.items():
            # Draw signal housing
            cv2.rectangle(img, (pos[0]-50, pos[1]-50), (pos[0]+50, pos[1]+50), (100, 100, 100), -1)
            
            if direction == active:
                color = (0, 255, 0)  # Green
                text = f"{green_remaining}s"
            elif direction == next_adjacent:
                color = (0, 255, 255)  # Yellow
                text = f"Wait: {red_remaining}s"
            else:
                color = (0, 0, 255)  # Red
                text = "RED"

            # Draw signal light
            cv2.circle(img, pos, 30, color, -1)
            cv2.circle(img, pos, 32, (255, 255, 255), 2)

            # Add direction label
            cv2.putText(img, direction, (pos[0]-30, pos[1]-70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Add timer text
            cv2.putText(img, text, (pos[0]-30, pos[1]+60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Add title
        cv2.putText(img, "Traffic Light Simulation", (250, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

        # Display the UI
        cv2.imshow("Traffic Light Simulation", img)

        # Wait for ESC key to exit
        if cv2.waitKey(1) == 27:
            cv2.destroyAllWindows()
            raise KeyboardInterrupt

    def process_intersection(self, images: Dict[str, str]) -> None:
        """Process all four directions at an intersection with enhanced error handling."""
        try:
            timers = {}
            logger.info("Starting traffic light simulation")

            # Count cars and calculate timers for each direction
            for direction, image_path in images.items():
                car_count, _ = self.count_cars(image_path)
                timers[direction] = self.calculate_timer(car_count)
                logger.info(f"{direction}: {car_count} vehicles detected, timer set to {timers[direction]}s")

            # Define circular order of traffic signals
            order = ['North', 'East', 'South', 'West']

            for cycle in range(self.config.max_cycles):
                logger.info(f"\nStarting cycle {cycle + 1}/{self.config.max_cycles}")
                
                for i in range(4):
                    active = order[i]
                    next_adjacent = order[(i + 1) % 4]
                    red_1 = order[(i + 2) % 4]
                    red_2 = order[(i + 3) % 4]

                    green_time = timers[active]
                    logger.info(f"\n{active} signal activated for {green_time} seconds")

                    # Countdown Timer for GREEN Light
                    for remaining_time in range(green_time, 0, -1):
                        try:
                            self.draw_traffic_ui(active, next_adjacent, timers, remaining_time, remaining_time)
                            logger.info(f"{active}: {remaining_time}s remaining")
                            time.sleep(1)
                        except KeyboardInterrupt:
                            logger.info("Simulation stopped by user")
                            return

                    logger.info(f"Switching from {active} to {next_adjacent}")

        except Exception as e:
            logger.error(f"Error in traffic light simulation: {e}")
        finally:
            cv2.destroyAllWindows()

def main():
    """Main function to run the traffic light simulation"""
    try:
        # Configuration
        config = TrafficConfig()
        
        # Initialize system
        traffic_system = TrafficLightSystem(config)
        
        # Define image paths using available images
        images = {
            'North': 'as.jpg',
            'East': 'asdas.jpg',
            'South': 'download (1).jpg',
            'West': 'download.jpg'
        }
        
        # Run simulation
        traffic_system.process_intersection(images)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
