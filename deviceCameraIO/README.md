## Device Camera I/O API

This repository contains code for interacting with the Device Camera I/O API this is not officially documented. The API allows you to activate or deactivate camera I/O operations.

## Prerequisites

Before using this code, make sure you have the following information:

- Active Brand Subdomain: Replace the `branding` variable with your Active Brand Subdomain. For example, if your subdomain is 'c019', update the variable to `branding = "c019"`. Using 'login' as the subdomain may introduce latency.

- Auth Key: Replace the `auth_key` variable with your Auth Key. This key should be in the format 'c019~aaa9282c7eff2c5e47a15e69f9b3c756'.

- Camera ID: Replace the `camera_id` variable with the ID of the camera you want to interact with.

## Usage

To use the code, follow these steps:

1. Set the required variables in the code as mentioned in the Prerequisites section.

2. Run the code.

3. The code will display a menu with the following options:
    - Activate Camera I/O
    - Deactivate Camera I/O
    - Exit

4. Enter the corresponding number for the desired action.

5. The code will make a request to the Device Camera I/O API and display the response.

# Payloads for activate and deactivate operations

```python
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
```
## Notes

- If the request is successful, the code will print the response from the API.

- If the request fails, the code will display the status code and the error message.

- To exit the program, enter '0' when prompted for a choice.

- The response of triggering the relay can vary due to bandwidth/camera or bridge status.
  In some situations I had the IO not responding to the request or responsing at a later time.

## ToDo

- Add configuring enabling the relay's. This script only shows how to trigger the relays.
- 

