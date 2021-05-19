from flask import Flask
import routes
import os

app = Flask(__name__)

#key = os.getenv("PRIVATE_KEY")


@app.route('/')
def status():
    status = routes.get_status()
    msg = '<html>'
    for item in status:
        msg += '<p>' + item + '</p>'
    msg += '</html>'
    return msg


# Routes for Control of Asynchronous Operations
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


@app.route('/get_trigger_amount')
def get_trigger_amount():
    trigger_amount = routes.get_trigger_amount()
    return f'Trigger amount: {trigger_amount}'

@app.route('/set_trigger_amount')
def set_trigger_amount():
    # Parameter for testing (parameters will be part of the route in future)
    amount = 100*10**18  # 100 tokens in smallest units

    trigger_amount = routes.set_trigger_amount(amount)
    return f'Trigger amount set to {trigger_amount}'

@app.route('/get_token_balance')
def get_token_balance():
    # Parameters for testing (parameters will be part of the route in future)
    token = '0xFB52FC1f90Dd2B070B9Cf7ad68ac3d68905643fa'  # Sea Token
    account = '0xaf72Fb3310561C0826fdF852c05bC50BF54989cd'  # Sea Token Charity Wallet

    balance = routes.get_token_balance(token=token, account=account)
    return f'Balance for the given account and token is: {balance}'


