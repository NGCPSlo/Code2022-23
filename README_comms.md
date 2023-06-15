# Communication Code

This README is for the following files and is concerned for developing the communication software needed for the MEA
- request_server.py
- coords_class.py
- coord_class_test.py
- main_multiproccessing.py
- db.json
- ngcp comms system design.draw.io
- Multi_process.svg

## Directions
How to run:
1. python request_server.py
2. python main_multiprocessing.python

3. edit coordinates in the database to see the changes


## Information about the communication code
coords_class.py is a packaged library that contains get and post functions needed for interacting with the json database

It's programmed in Python and utilizes the Flask micro-web framework

As for main_multiproccessing.py that file contains the integration code and boiler plate code for running the seperate features of the MEA.

Ideally for each of the functions, you just have to place your code inside it.

To see how this work at a system design level, look at the following files
- ngcp comms system design.draw.io
- Multi_process.svg

Integration Code for the Medical Evacuation Aircraft(MEA) was meant to be run with multiprocessing

Multiproccessing was chosen over multithreading because python has a Global Interpreter Lock(GIL) for multi-threading and so operations can't run in parallel.
Multiprocessing doesn't have a GIL so running multiple operations in parallel is possible

