## APSERa Monitor

APSERa monitor helps the user to conveniently operate the Cryotel-MT cooler via the AVC controller. It is coded in python, and the user needs the following libraries (if not there) - Tkinter, serial, datetime (not DateTime!). 
                                                                                                                                                                       
For runing, download the Cryotel_controller_GUI.py and open terminal in its download directory and run it using: 
``` python Cryotel_controller_GUI.py  ```  

The application is being constantly improved. So keep checking this space.

| Version | Date pushed | Description of changes |
| ------------- | ------------- | ------------- |
| 1.0  | 30/05/2024  | First version ||
| 1.1  | 6/6/2024    | Added Kp, Ki, Kd control, added refresh buttons, system parameters update every 5 secs|
| 1.2  | 7/6/2024    | added Update button for auto off, changed visuals, some internal logic, added port and Baudrate input option for user at launch; a minor change was made on June 28 2024, fixing a bug in serial comm|
