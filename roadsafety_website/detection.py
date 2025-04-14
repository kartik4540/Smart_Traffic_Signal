import cv2
import numpy as np
from detection import AccidentDetectionModel
import requests
from requests.auth import HTTPBasicAuth
import time
import random
import urllib.parse
import os

# Twilio credentials
account_sid = 'twilio id'
auth_token = 'twilio token'
twilio_phone_number = '+13267778589'
# Format phone numbers with proper international format
first_recipient_phone_number = '+91'  # First emergency contact
second_recipient_phone_number = '+91'  # Second emergency contact

addresses = [
    "123 Main St, Springfield",
    "456 Elm St, Shelbyville",
    "789 Oak St, Capital City",
    "101 Maple St, Ogdenville"
]

def generate_twiml_url():
    random_address = random.choice(addresses)
    address_message = f"The address of the accident is {random_address}."
    address_url = f"http://twimlets.com/message?Message%5B0%5D={urllib.parse.quote(address_message)}"
    forward_url = f"http://twimlets.com/forward?PhoneNumber={urllib.parse.quote(second_recipient_phone_number)}"
    gather_url = (
        "http://twimlets.com/gather?"
        "Message%5B0%5D=Emergency%20call%20to%20Kartik%20as%20fast%20as%20possible.%20"
        "Press%201%20for%20the%20address%20of%20the%20accident.%20"
        "Press%202%20to%20forward%20the%20call%20to%20the%20next%20person.&"
        f"NumDigits=1&"
        f"1={urllib.parse.quote(address_url)}&"
        f"2={urllib.parse.quote(forward_url)}"
    )
    return gather_url

def make_phone_call(to_phone_number, from_phone_number, twiml_url):
    try:
        url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json'
        data = {
            'Url': twiml_url,
            'To': to_phone_number,
            'From': from_phone_number,
            'StatusCallback': twiml_url  # Add status callback URL
        }
        response = requests.post(url, data=data, auth=HTTPBasicAuth(account_sid, auth_token))
        if response.status_code == 201:
            print(f"Call initiated successfully to {to_phone_number}!")
            return response.json()['sid']
        else:
            print(f"Failed to initiate call. Status code: {response.status_code}")
            print(f"Error message: {response.text}")
            return None
    except Exception as e:
        print(f"Error making call: {str(e)}")
        return None

def handle_emergency_call():
    print("Initiating emergency call sequence...")
    twiml_url = generate_twiml_url()
    call_sid = make_phone_call(first_recipient_phone_number, twilio_phone_number, twiml_url)

    if call_sid:
        time.sleep(30)
        call_status = requests.get(
            f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls/{call_sid}.json',
            auth=HTTPBasicAuth(account_sid, auth_token)
        ).json().get('status', '')

        if call_status not in ['completed', 'answered']:
            print("First call not acknowledged. Calling second recipient...")
            make_phone_call(second_recipient_phone_number, twilio_phone_number, generate_twiml_url())

def main():
    try:
        # Load the model
        print("Attempting to load the accident detection model...")
        model = AccidentDetectionModel('C:/Users/91989\Desktop\KARTIK/random project/traffic signal/roadsafety_website/model.json', r'C:\Users\91989\Desktop\KARTIK\random project\traffic signal\roadsafety_website\model_weights.h5')
        print("Model loaded successfully!")

        # Open video file
        video_path = r'roadsafety_website/acc1.mp4'
        print(f"Opening video file: {video_path}")
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print("Error: Could not open video file")
            return

        print("Processing video for accident detection...")
        accident_detected = False  # Flag to track if we've already detected an accident
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to RGB and resize
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            roi = cv2.resize(rgb_frame, (250, 250))

            # Make prediction
            pred, prob = model.predict_accident(roi[np.newaxis, :])
            confidence = prob[0][0] * 100  # Convert to percentage

            # Only show prediction if confidence is above 90%
            if confidence > 90:
                # Draw rectangle and text
                cv2.rectangle(frame, (10, 10), (400, 60), (0, 0, 255), 2)
                cv2.putText(frame, f"Accident Detected! Confidence: {confidence:.2f}%", 
                          (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # If this is the first time we've detected an accident, make the emergency call
                if not accident_detected:
                    handle_emergency_call()
                    accident_detected = True

            # Display the frame
            cv2.imshow('Accident Detection', frame)

            # Break loop on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        print("Video processing completed.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
