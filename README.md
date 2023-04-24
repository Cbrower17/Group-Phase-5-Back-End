# Sytax Slingers Group Project Back End

## Overview


## Setup / Running the Project (on Windows)
Enter you terminal (however you have set up to do so.)
    Make sure you can run 2 terminals for this. 

### Check Python version
Type: python --version
If you are running Python 3.9.2 or higher you can skip the next section

### Install the correct python. 
Navigate to the following website and follow the instructions to install Python 3 on your system
For Windows:
https://docs.python.org/3/using/windows.html
For Mac:
https://docs.python.org/3/using/mac.html
For Unix (ie: Linux):
https://docs.python.org/3/using/unix.html

### Install the Virtual Environment
In your terminal, navigate to the root directory of this project:

Python/Flask:
Type: pipenv install
(it can take a little while, so please be patient)
Type: pipenvshell to enter the virtual environment
cd into server
Run the following commands:
    export FLASK_APP=app.py
    export FLASK_RUN_PORT=5555
    flask db init
    flask db revision --autogenerate -m 'Create tables' 
    flask db upgrade 
    chmod +x seed.py (to unlock permisions)
    python seed.py (wait a moment)
        If any of these give a hiccup, you can delete the instance and migration folders and run these again.
    chmod +x app.py (to unlock permisions) 

Next.js:
cd into client
Run the following Commands:
    ???

Congrats, you are now configured and ready to run this program!

## Instructions:
### How to Start the program
Python/Flask:
from the server folder run:
    python app.py

React:
in a second terminal:
from the client folder run:
    npm run start
    ???

And it begins!

### How to access the programs Functions:
TBD


## Assignment Goals
TBD


## Project Pitch/Ideas. 
TBD