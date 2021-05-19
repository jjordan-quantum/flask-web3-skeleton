from flask import Flask
import routes
import os

app = Flask(__name__)

#key = os.getenv("PRIVATE_KEY")

@app.route('/')
def home():
    return routes.get_status()

# Routes for Asynchronous Operations
#-------------------------------------------

@app.route('/start')
def start_process():
    return routes.start_process()

@app.route('/stop')
def stop_process():
    return routes.stop_process()

@app.route('/pause')
def pause_process():
    return routes.pause_process()

@app.route('/unpause')
def unpause_process():
    return routes.unpause_process()

# Routes for Specific functions
#-------------------------------------------


