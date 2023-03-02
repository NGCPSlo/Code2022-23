# How to Run a Drone Path Simulation on QGroundControl
## Pre-reqs
- Windows
- Python 3.11
- QGroundControl

## Directions
1. Open up drone_client.py in your IDE
	- Pull NGCPSlo / Code2022-23 repository from GitHub.

2. Open up command prompt
	- Run 'pip install paho-mqtt'
	- Run 'pip install dronekit'
	- Run 'pip install dronekit-sitl -UI'
	- Run 'dronekit-sitl -UI'

3. Open QgroundControl
	- Click Q on the top left
	- Click Application Setting
	- Click Comm Links
	- Click Add
		- Enter Name ('Test')
		- Change Type tdssdso TCP
		- Change Server Address to 127.0.0.1 (local address on pc)
		- Change Port to 5760 or whatever Bind port is
	- Click Test
	- Click Connect
	
5. Go back to QGroundControl
	- Click back: should be on the page with the map showing testing site on Monaro Hwy
	- Click on stabilized
	- Change stabilized to Guided

6. Run 'python drone_client.py' (in command line or preferred IDE)

https://dronekit-python.readthedocs.io/en/latest/develop/installation.html
