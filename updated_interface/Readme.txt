                   APSERa SOP for Updated Control Interface

The updated control interface involves three files located in the test_codes folder:

- upd_cryotel_f.py     : Controls the backend of the interface.
- upd_index.html       : Controls the frontend of the interface.
- config.yml           : Stores all variable values used by the above two files.

-----------------------------------------------------------------------
Running the ACI Interface

Navigate to the /home/swan/apsera/test_codes folder. You will find:

- upd_cryotel_f.py
- config.yml

The upd_index.html file is located inside the templates folder.

To run the Flask web application, open a terminal in this directory and execute:

    python upd_cryotel_f.py

- Press Ctrl and click on the web address displayed in the terminal to launch the interface.
- Press Ctrl+C in the terminal to stop the server.

-----------------------------------------------------------------------
System Status Box

A new System Status Box has been added in the updated interface. It displays
the connection status of the following systems:

    - Lakeshore
    - Cryogenic
    - IIA
    - Power

Each system’s connection status is shown using color indicators:
    - Green : Connected
    - Red   : Disconnected

-----------------------------------------------------------------------
Alert System

An alert system has been integrated into the interface. It displays an alert 
window under the following conditions:

    - When sensor values exceed predefined threshold limits.
    - When any system gets disconnected or reconnected.

The alert window includes:
    - The alert message
    - Input fields for the user's name and comment

Alerts will reappear at fixed intervals if the issue still persists.
These intervals can be configured in the config.yml file.

The time interval is calculated between the timestamp when an alert is
acknowledged and when it is shown again.

All alert logs are stored in CSV format and include the following details:

    - Alert ID
    - Alert message
    - Timestamp of alert trigger
    - Timestamp of alert acknowledgment
    - Name and comment of the user

-----------------------------------------------------------------------
All the Logs of IIA,lakeshore,power,cryo are stored in .txt files in the following directory:

    /home/swan/apsera/test_codes/cryorun_logs

The files updates the logs in real time.

-----------------------------------------------------------------------
About the config.yml File

The config.yml file is the centralized configuration for the control and 
alert system. Each section defines device-specific parameters such as:

    - USB paths
    - Data polling intervals
    - Alert thresholds
    - Re-alert intervals for disconnections or breaches

You can edit any parameter directly in this file as needed.
Inline comments are provided for clarity.

To enable or disable the entire alert system, use:

    alertstatus : 0    # 0 for OFF, 1 for ON

-----------------------------------------------------------------------
USB Path Configuration

USB devices are referenced using their unique by-path addresses like:

    /dev/serial/by-path/pci-0000:00:14.0-usb-0:9.2:1.0-port0

These paths typically remain consistent even if the USB device is unplugged 
and plugged back in.

NOTE: If the entire USB hub is disconnected and reconnected, these USB path 
numbers might change.

To list current USB path mappings, run in terminal:

    ls -l /dev/serial/by-path/

Example output:

    lrwxrwxrwx 1 root root 13 Jul 16 11:07 pci-0000:00:14.0-usb-0:9.1:1.0-port0 -> ../../ttyUSB4
    lrwxrwxrwx 1 root root 13 Jul 16 10:43 pci-0000:00:14.0-usb-0:9.2:1.0-port0 -> ../../ttyUSB3
    lrwxrwxrwx 1 root root 13 Jul 14 17:28 pci-0000:00:14.0-usb-0:9.3:1.0-port0 -> ../../ttyUSB0
    lrwxrwxrwx 1 root root 13 Jul 15 14:51 pci-0000:00:14.0-usb-0:9.4:1.0-port0 -> ../../ttyUSB1
    lrwxrwxrwx 1 root root 13 Jul 15 14:51 pci-0000:00:14.0-usb-0:9.4:1.0-port1 -> ../../ttyUSB2

To determine which USB number corresponds to which device, run:

    dmesg | grep ttyUSB

Update the appropriate USB path in config.yml using the path, like:

    "/dev/serial/by-path/pci-0000:00:14.0-usb-0:9.2:1.0-port0"

-----------------------------------------------------------------------
IP Address Change

In rare cases, if your system’s IP address changes, the web app might not load.

To fix this, update the IP address at the very end of the upd_cryotel_f.py file.
Look for the following line:

    app.run(debug=False, host='172.16.101.85', port=5002)

Replace the IP address ('172.16.101.85') with your current IP.

