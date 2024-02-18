"""
Reads UNVR camera configuration and generates an HTML page with grid layout of RTSP streams from the cameras using RTSPtoWebServer.

Reads the camera configuration from the UNVR using the API. Retrieves the RTSP stream URLs for each camera. Generates a JSON configuration file for RTSPtoWebServer with the camera RTSP streams. Writes an HTML page with grid layout of <video> elements, with hidden input elements containing the WebRTC stream URL from RTSPtoWebServer for each camera. Saves the JSON config and HTML page to disk.
"""
import sys
import json
import requests
import os.path
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress SSL certificate verification warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

"""
Reads the camera configuration from the given JSON file.

Parameters:
    filename (str): Path to the JSON file containing the camera configuration.
                    Default is "streamsconfig.json".

Returns:
    dict: The camera configuration loaded from the JSON file.
"""
def read_config(filename="streamsconfig.json"):
    if not os.path.exists(filename):
        username = input("Enter UNVR username: ")
        password = input("Enter UNVR password: ")
        UNVR_IP = input("Enter UNVR IP: ")
        RTSPW_IP = input("Enter RTSPtoWeb Server IP: ")
        config = {
            "username": username,
            "password": password,
            "UNVR_IP": UNVR_IP,
            "RTSPW_IP": RTSPW_IP
        }
        with open(filename, "w") as f:
            json.dump(config, f, indent=2)
    else:
        with open(filename, "r") as f:
            config = json.load(f)
    return config

"""
Reads UNVR camera configuration and generates an HTML page with grid layout of RTSP streams from the cameras using RTSPtoWebServer.

This module contains the main logic to:
- Login to the UNVR and get the session cookie
- Make an authenticated request to get the list of cameras 
- Extract the RTSP stream URL for each camera
- Generate a JSON configuration file for the RTSPtoWebServer with the camera streams
- Generate an HTML page with grid layout of video elements for each camera stream
- Save the JSON config and HTML page to disk
"""
def main():
    username = config["username"]
    password = config["password"]
    UNVR_IP = config["UNVR_IP"]
    
    # Login and get session cookie
    session_cookie = login(username, password, UNVR_IP)
    if session_cookie:
        # Example authenticated request
        camera_list_url = f"https://{UNVR_IP}/proxy/protect/api/bootstrap"
        cameras = make_authenticated_request(camera_list_url, session_cookie)
        if cameras:
            # Add additional structure
            complete_json = {
                "channel_defaults": {},
                "server": {
                    "debug": True,
                    "http_debug": False,
                    "http_demo": True,
                    "http_dir": "web",
                    "http_login": "demo",
                    "http_password": "demo",
                    "http_port": ":8083",
                    "https": False,
                    "https_auto_tls": False,
                    "https_auto_tls_name": "",
                    "https_cert": "server.crt",
                    "https_key": "server.key",
                    "https_port": ":443",
                    "ice_credential": "",
                    "ice_servers": [
                        "stun:stun.l.google.com:19302"
                    ],
                    "ice_username": "",
                    "log_level": "debug",
                    "rtsp_port": ":5541",
                    "token": {
                        "backend": "http://127.0.0.1/test.php",
                        "enable": False
                    },
                    "webrtc_port_max": 0,
                    "webrtc_port_min": 0
                },
                "streams": {}
            }
            
            # Fill streams in the JSON data
            for camera in cameras['cameras']:
                camera_name = camera['name']
                camera_namens = camera_name.replace(' ', '')
                channels = camera['channels']
                for channel in channels:
                    if channel['id'] == 2:
                        rtsp_alias = channel['rtspAlias']
                stream_url = f"rtsps://{UNVR_IP}:7441/{rtsp_alias}"
                complete_json["streams"][camera_namens] = {
                    "channels": {
                        "0": {
                            "on_demand": True,
                            "insecure_skip_verify": True,
                            "url": stream_url
                        }
                    },
                    "name": camera_name
                }
            
            # Write complete JSON data to a file
            with open('config.json', 'w') as json_file:
                json.dump(complete_json, json_file, indent=2)
            
            print("Complete JSON data saved to config.json, Please copy this file to the RTSPtoWeb Server, then run the service")
            print("GO111MODULE=on go run *.go")
            # Create the HTML content
            html_content = "<!DOCTYPE html>\n<html>\n<head>\n<title>Cams</title>\n<style>\n  /* Define the grid layout */\n  .grid-container {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(1px,  400px)); /* Adjust minmax values as needed */\n    gap: 10px; /* Adjust the gap between grid items */\n  }\n\n  /* Make videos responsive within the grid */\n  .mse-video {\n    width: 100%;\n    height: 100%;\n    object-fit: cover; /* Ensure the video fills the grid item */\n  }\n\n  /* Media queries to adjust grid layout for different screen sizes */\n  @media screen and (max-width: 1920px) {\n    .grid-container {\n      grid-template-columns: repeat(auto-fit, minmax(1px, 500px)); /* Adjust minmax values as needed */\n    }\n  }\n</style>\n</head>\n<body>\n<div class=\"grid-container\">"

            for key, value in complete_json["streams"].items():
                name_without_spaces = key.replace(' ', '')
                html_content += f"\n   <input type=\"hidden\" name=\"mse-url\" class=\"mse-url\" value=\"ws://{config['RTSPW_IP']}:8083/stream/{name_without_spaces}/channel/0/mse?uuid=demo&channel=0\">\n"
                html_content += f"   <video class=\"mse-video\" autoplay muted playsinline controls style=\"max-width: 100%; max-height: 100%;\"></video>\n"

            html_content += "\n</div><script src=\"main.js\"></script>\n</body>\n</html>"

            # Write the HTML content to a file
            with open('Cameras.html', 'w') as output_file:  
                output_file.write(html_content)
                
            print("HTML file saved as Cameras.html, copy Cameras.html and Main.js to a computer with access to the RTSPtoWeb server.")
        else:
            print("Failed to fetch camera list")
    else:
        print("Unable to obtain session cookie")


"""Logs into the UNVR device to get an auth token.

Args:
  username: The username for the UNVR device.
  password: The password for the UNVR device.
  UNVR_IP: The IP address of the UNVR device.

Returns:
  The auth token if login succeeded, None otherwise.
"""
def login(username, password, UNVR_IP):
    login_url = f'https://{UNVR_IP}/api/auth/login'
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(login_url, json=data, verify=False)
    if response.status_code == 200:
        session_cookie = response.cookies.get("TOKEN")
        return session_cookie
    else:
        print("Login failed")
        return None


"""Makes an authenticated API request to the UNVR device.

Args:
  url: The API endpoint URL to make the request to.
  session_cookie: The auth token from logging in.

Returns:
  The JSON response if the request succeeded, None otherwise.
"""
def make_authenticated_request(url, session_cookie):
    headers = {
        "Cookie": f"TOKEN={session_cookie}"
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        print("Request failed")
        return None

if __name__ == "__main__":
    config = read_config()
    main()
