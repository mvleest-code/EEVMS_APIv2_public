import requests
import json

# add your Active Brand Subdomain, Auth Key, and Camera ID here
branding = ""  # This should be the Active Brand Subdomain like 'c019', using 'login' will add latency
auth_key = ""  # This should give you the auth_key like 'c019~aaa9282c7eff2c5e47a15e69f9b3c756'
camera_id = ""

# Base URL for API requests
BASE_URL = f"https://{branding}.eagleeyenetworks.com/g/device"

# Headers for the request including the Cookie
headers = {
    "Content-Type": "application/json",
    "Cookie": f"auth_key= {auth_key}",
}

# Function to send POST request
def make_request(payload):
    response = requests.post(BASE_URL, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("Request successful.")
        print(response.json())  # Or any other response handling
    else:
        print(f"Failed to make request. Status code: {response.status_code}")
        print(response.text)

# Payloads for activate and deactivate operations
import json

def get_payload_activate_io(camera_id):
    settings = {
        "settings": {
            "camera_io_output_state": {
                "relay_1": {
                    "state": "active"
                }
            }
        }
    }
    return {
        "id": camera_id,
        "camera_settings_add": json.dumps(settings)
    }

def get_payload_deactivate_io(camera_id):
    settings = {
        "settings": {
            "camera_io_output_state": {
                "relay_1": {
                    "state": "idle"
                }
            }
        }
    }
    return {
        "id": camera_id,
        "camera_settings_add": json.dumps(settings)
    }

def main():
    while True:
        print("\nMenu:")
        print("1. Activate Camera I/O")
        print("2. Deactivate Camera I/O")
        print("0. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            payload = get_payload_activate_io(camera_id)
            make_request(payload)
        elif choice == "2":
            payload = get_payload_deactivate_io(camera_id)
            make_request(payload)
        elif choice == "0":
            print("Exiting...")
            break  # This should only be executed when choice is "0"
        else:
            print("Invalid choice, please enter 1, 2, or 0.")

if __name__ == "__main__":
    main()

