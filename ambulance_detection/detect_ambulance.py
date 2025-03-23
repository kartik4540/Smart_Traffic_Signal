import cv2
import numpy as np
from ultralytics import YOLO
import argparse
import time

# Add cooldown tracking
ambulance_cooldown = {
    'North': 0,
    'South': 0,
    'East': 0,
    'West': 0
}

def check_emergency_features(img):
    """Check for red emergency lights in the image"""
    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define red color range in HSV
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    # Create masks for red color
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 + mask2
    
    # Count red pixels
    red_pixels = np.sum(red_mask > 0)
    total_pixels = img.shape[0] * img.shape[1]
    red_ratio = red_pixels / total_pixels
    
    return red_ratio > 0.01  # Return True if more than 1% of pixels are red

def process_image(img, model, conf_threshold):
    """Process a single image and detect ambulances"""
    # Resize image to standard size
    img = cv2.resize(img, (640, 416))
    
    # Run YOLO detection
    results = model(img, conf=conf_threshold)
    
    # Get detection results
    detections = results[0].boxes.data.cpu().numpy()
    
    # Draw detections
    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        if conf >= conf_threshold:
            # Draw bounding box
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            # Add label
            label = f'Ambulance {conf:.2f}'
            cv2.putText(img, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Display image
    cv2.imshow('Ambulance Detection', img)
    cv2.waitKey(1)
    
    return len(detections) > 0

def create_traffic_display(width=800, height=600):
    """Create a black background display with traffic signal positions"""
    display = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add title
    cv2.putText(display, "Traffic Light Simulation", (width//4, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
    
    return display

def draw_traffic_light(display, position, color, direction, timer=None, status=""):
    """Draw a traffic light circle with direction label and timer"""
    # Draw grey background box
    box_size = 80
    x, y = position
    cv2.rectangle(display, (x-box_size//2, y-box_size//2), 
                 (x+box_size//2, y+box_size//2), (128, 128, 128), -1)
    
    # Draw circle (traffic light)
    radius = 30
    if color == "red":
        circle_color = (0, 0, 255)  # BGR Red
    elif color == "yellow":
        circle_color = (0, 255, 255)  # BGR Yellow
    else:  # green
        circle_color = (0, 255, 0)  # BGR Green
    
    cv2.circle(display, (x, y), radius, circle_color, -1)
    cv2.circle(display, (x, y), radius, (255, 255, 255), 2)  # White border
    
    # Add direction label
    cv2.putText(display, direction, (x-30, y-50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Add timer if provided
    if timer is not None:
        cv2.putText(display, f"{timer}s", (x-15, y+box_size), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Add status if provided
    if status:
        cv2.putText(display, status, (x-30, y+box_size+30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def traffic_signal_cycle(images, model, conf_threshold, cycle_duration):
    """Run traffic signal cycle with ambulance detection"""
    # Define directions in order of rotation (East → South → West → North)
    directions = ['East', 'South', 'West', 'North']
    signal_duration = 10  # Fixed 10 seconds for each signal
    cooldown_duration = 30  # 30 seconds cooldown after ambulance detection
    
    # Window setup
    cv2.namedWindow('Traffic Light Simulation', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Traffic Light Simulation', 800, 600)
    
    # Traffic light positions (center points)
    positions = {
        'North': (400, 150),  # Top
        'South': (400, 450),  # Bottom
        'East': (650, 300),   # Right
        'West': (150, 300)    # Left
    }
    
    try:
        while True:
            # First check all directions for ambulance
            print("\n=== Checking all directions for ambulance... ===")
            ambulance_detected = False
            
            # Update cooldown timers
            current_time = time.time()
            for direction in directions:
                if ambulance_cooldown[direction] > 0:
                    ambulance_cooldown[direction] = max(0, ambulance_cooldown[direction] - 1)
                    print(f"{direction} direction cooldown: {ambulance_cooldown[direction]}s")
            
            # Check each direction for ambulance
            for i, (direction, img_path) in enumerate(zip(directions, images)):
                print(f"\nChecking {direction} direction for ambulance...")
                try:
                    # Skip if direction is in cooldown
                    if ambulance_cooldown[direction] > 0:
                        print(f"Skipping {direction} direction due to cooldown")
                        continue
                        
                    img = cv2.imread(img_path)
                    if img is None:
                        print(f"Error: Could not read image for {direction} direction")
                        continue
                    
                    # Check for ambulance
                    if process_image(img, model, conf_threshold):
                        print(f"\n🚨 AMBULANCE DETECTED IN {direction} DIRECTION!")
                        ambulance_detected = True
                        ambulance_cooldown[direction] = cooldown_duration  # Set cooldown
                        
                        # Give immediate green signal to ambulance direction
                        for remaining_time in range(signal_duration, -1, -1):
                            display = create_traffic_display()
                            for d in directions:
                                if d == direction:
                                    # Current green signal (ambulance direction)
                                    color = "green"
                                    status = "EMERGENCY GREEN"
                                    timer = remaining_time
                                elif d == directions[(i + 1) % 4]:
                                    # Next signal
                                    color = "red"
                                    status = "NEXT"
                                    timer = remaining_time
                                else:
                                    # Other signals
                                    color = "red"
                                    status = "STOP"
                                    timer = None
                                
                                draw_traffic_light(display, positions[d], color, d, timer, status)
                            
                            cv2.imshow('Traffic Light Simulation', display)
                            cv2.waitKey(1000)  # Update every second
                        break
                        
                except Exception as e:
                    print(f"Error processing {direction} direction: {e}")
            
            if not ambulance_detected:
                print("\n=== Running normal cycle ===")
                print("Sequence: East → South → West → North")
                
                # Normal cycle
                for i, direction in enumerate(directions):
                    # Skip if direction is in cooldown
                    if ambulance_cooldown[direction] > 0:
                        print(f"Skipping {direction} direction due to cooldown")
                        continue
                        
                    # 10 second countdown for current green signal
                    for remaining_time in range(signal_duration, -1, -1):
                        display = create_traffic_display()
                        
                        # Update all traffic lights
                        for j, d in enumerate(directions):
                            if d == direction:
                                # Current green signal
                                color = "green"
                                status = "GO"
                                timer = remaining_time
                            elif d == directions[(i + 1) % 4]:
                                # Next signal
                                color = "yellow"
                                status = "NEXT"
                                timer = remaining_time
                            else:
                                # Other signals
                                color = "red"
                                status = "STOP"
                                timer = None
                            
                            draw_traffic_light(display, positions[d], color, d, timer, status)
                        
                        cv2.imshow('Traffic Light Simulation', display)
                        cv2.waitKey(1000)  # Update every second
            
    except KeyboardInterrupt:
        print("\nTraffic signal cycle stopped by user")
    finally:
        cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description='Detect ambulances in images and manage traffic signals')
    parser.add_argument('--source', type=str, help='Path to image file or "0" for webcam')
    parser.add_argument('--conf', type=float, default=0.85, help='Confidence threshold for detection')
    parser.add_argument('--east', type=str, default="C:/Users/91989/Desktop/KARTIK/traffic signal/vehicle_detection/as.jpg", help='Path to east direction image')
    parser.add_argument('--south', type=str, default="C:/Users/91989/Desktop/KARTIK/traffic signal/vehicle_detection/download.jpg", help='Path to south direction image')
    parser.add_argument('--west', type=str, default="C:/Users/91989/Desktop/ambu.jpeg", help='Path to west direction image')
    parser.add_argument('--north', type=str, default="C:/Users/91989/Desktop/KARTIK/traffic signal/vehicle_detection/asdas.jpg", help='Path to north direction image')
    parser.add_argument('--cycle', type=int, default=30, help='Total cycle duration in seconds')
    args = parser.parse_args()

    # Load YOLO model
    try:
        model = YOLO('best.pt')
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        return

    if args.source:
        # Single image or webcam mode
        if args.source == "0":
            # Webcam mode
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Error: Could not open webcam")
                return
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                process_image(frame, model, args.conf)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
        else:
            # Single image mode
            try:
                img = cv2.imread(args.source)
                if img is None:
                    print(f"Error: Could not read image file: {args.source}")
                    return
                process_image(img, model, args.conf)
            except Exception as e:
                print(f"Error processing image: {e}")
    else:
        # Traffic signal cycle mode
        images = [args.east, args.south, args.west, args.north]  # Order: East → South → West → North
        traffic_signal_cycle(images, model, args.conf, args.cycle)

if __name__ == "__main__":
    main() 