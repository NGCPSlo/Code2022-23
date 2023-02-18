# How to Run a Drone Path Simulation on QGroundControl
## Pre-reqs
- Windows
- Python 3.11
- QGroundControl

1. Open up drone_client.py in your IDE
	a. Pull NGCPSlo / Code2022-23 repository from GitHub.
2. Open up command prompt
	a. Run 'pip install paho-mqtt'
	b. Run 'pip install dronekit'
	c. Run 'pip install dronekit-sitl -UI'
	d. Run 'dronekit-sitl -UI'

https://dronekit-python.readthedocs.io/en/latest/develop/installation.html

4. Open QgroundControl
	a. Click Q on the top left
	b. Click Application Setting
	c. Click Comm Links
		i. 		Click Add
		ii. 	Enter Name ('Test')
		iii.	Change Type tdssdso TCP
		iv.		Change Server Address to 127.0.0.1 (local address on pc)
		v.		Change Port to 5760 or whatever Bind port is

5. Click test
	a. Click Connect
	
6. Go back to QGroundControl
	a. Click back: should be on the page with the map showing testing site on Monaro Hwy
	b. Click on stabilized
	c. Change stabilized to Guided

7. Run 'python drone_client.py' (in command line or preferred IDE)
