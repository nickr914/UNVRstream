# UNVRstream
It's frustrating that Ubiquit seems unresponsive, and the Viewer tool doesn't quite live up to its name. Additionally, managing multiple users accessing the Ubiquit UNVR for camera viewing causes the CPU usage to soar. After investing nine tedious hours in troubleshooting software and exploring the UNVR device, I concluded that a solution lies in streamlining the process. By consolidating stream capture and distribution through a single device, we can potentially resolve this issue.

This uses RTSPtoWeb from deepch.

![Cams](https://github.com/nickr914/UNVRstream/assets/7483972/8fa487bf-75b6-4a9d-a31e-575de1511a1e)

# UNVR Camera Configuration to HTML Page Conversion

This script reads UNVR camera configuration and generates an HTML page with a grid layout of RTSP streams from the cameras using RTSPtoWeb Server from https://github.com/deepch/RTSPtoWeb.

## Installation


Ensure you have Python installed. This script requires Python 3.

Clone the repository:

gh repo clone nickr914/UNVRstream

Install the required packages:

pip install requests

Usage

    Log into your UNVR device:
        Go to your UNVR device's IP address.
        Log in using your username and password.
        Navigate to Protect.
        Click on UniFi Devices.
        Select a camera.
        Click on Settings.
        Navigate to Advanced.
        Ensure Low Resolution is selected.

    Run the script and it will ask you for the username and password to the UNVR device, the IP for the device, and the IP for the RTSPtoWeb Server:

python getUNVRstreams.py

Description

This script performs the following tasks:

    Logs into the UNVR device to get the session cookie.
    Makes an authenticated request to get the list of cameras.
    Extracts the RTSP stream URL for each camera.
    Generates a JSON configuration file for RTSPtoWebServer with the camera streams.
    Generates an HTML page with a grid layout of video elements for each camera stream.
    Saves the JSON config and HTML page to disk.

Example


python getUNVRstreams.py

This will generate the necessary configuration files and HTML page for the specified RTSPtoWebServer IP address.
Copy the config.json from this directory, to the RTSPtoWeb server directory, replacing the stock config.json.
Copy the Cameras.html and Main.js files to a machine to display the grid.

You can always change the HTML, I do not make pretty, I make functional.

Any questions send then to the circular filing cabinet.

Authors

    Your Nick R

License

This project is licensed under the MIT License - see the LICENSE file for details.

This version provides clear instructions on setting up the configuration file before runn
