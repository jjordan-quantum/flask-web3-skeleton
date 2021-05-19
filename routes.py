from web3 import Web3
import re
import json
import time
from threading import Thread
import asyncio
import lib.abis as abis

# global variables

# web3 variables
web3 = None
global_provider = 'https://bsc-dataseed.binance.org/'
web3_count = 0

# async command flags
pause = False
kill = False
running = False
DELAY = 1 # in seconds

# trigger amount for async loop to execute functions
trigger_amount = 200000000000000000000000000
SEA_TOKEN_TOTAL_SUPPLY = 200000000000000000000000000

# for testing
loop_count = 0

# Addresses for SEA TOKEN
SEA_TOKEN_ADDRESS = '0xFB52FC1f90Dd2B070B9Cf7ad68ac3d68905643fa'
SEA_TOKEN_CHARITY_WALLET = '0xaf72Fb3310561C0826fdF852c05bC50BF54989cd'

# note: PancakeSwap V1 addresses
MASTERCHEF_ADDRESS = '0x73feaa1eE314F8c655E354234017bE2193C9E24E'
FACTORY_ADDRESS_V1 = '0xBCfCcbde45cE874adCB698cC183deBcF17952812'
ROUTER_ADDRESS_V1 = '0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F'

# note: PancakeSwap V2 addresses
FACTORY_ADDRESS_V2 = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'
ROUTER_ADDRESS_V2 = '0x10ED43C718714eb63d5aA57B78B54704E256024E'

masterchef_abi = json.loads(abis.masterchef_abi)
with open("lib/IUniswapV2Factory.json", 'r') as read_file:
    factory_abi = json.load(read_file)['abi']
with open("lib/IUniswapV2Router02.json", 'r') as read_file:
    router_abi = json.load(read_file)['abi']
with open("lib/IUniswapV2ERC20.json", 'r') as read_file:
    erc20_abi = json.load(read_file)['abi']
with open("lib/IUniswapV2Pair.json", 'r') as read_file:
    pair_abi = json.load(read_file)['abi']
with open("lib/pairs.json", 'r') as read_file:
    pairs = json.load(read_file)
with open("lib/pools.json", 'r') as read_file:
    pools = json.load(read_file)
with open("lib/tokens.json", 'r') as read_file:
    tokens = json.load(read_file)

# Functions for process control command routes
#----------------------------------------------


def get_status():

    global loop_count
    global pause
    global running
    global web3_count
    global trigger_amount
    balance = _get_token_balance(token=SEA_TOKEN_ADDRESS, account=SEA_TOKEN_CHARITY_WALLET)
    balance_over_trigger_amount = balance >= trigger_amount
    return [f'Current Server Status: ',
            f'Running: {running}',
            f'Paused: {pause}',
            f'Total loop count: {loop_count}',
            f'Total web3 count: {web3_count}',
            f'Trigger amount: {trigger_amount}',
            f'Balance of charity wallet: {balance}',
            f'Current balance greater than trigger amount: {balance_over_trigger_amount}']


def start_process():

    global running
    if not running:
        _reset_trigger_amount()
        running = True
        thread_1 = Thread(target=runner)
        thread_1.start()
        return 'Process starting...'
    else:
        return 'Process already running.'


def stop_process():

    global running
    global kill
    if running:
        kill = True
        return 'Killing process...'
    else:
        return 'Process not running.'


def pause_process():

    global pause
    if pause:
        return 'Process already paused.'
    else:
        pause = True
        return 'Pausing process....'


def unpause_process():

    global pause
    if not pause:
        return 'Process is not paused.'
    else:
        pause = False
        return 'Unpausing process...'

# Functions for interacting with async loop
#----------------------------------------------


def get_trigger_amount():

    global trigger_amount
    return trigger_amount


def set_trigger_amount(new_trigger_amount):

    global trigger_amount
    trigger_amount = new_trigger_amount
    return trigger_amount

def _reset_trigger_amount():
    global trigger_amount
    global SEA_TOKEN_TOTAL_SUPPLY
    trigger_amount = SEA_TOKEN_TOTAL_SUPPLY


# Functions for account / smart contract info routes
#----------------------------------------------



def get_token_balance(token, account):

    #print(f'In get_token_balance with params: \n{token}, \n{account}')
    balance = _get_token_balance(token=token, account=account)
    return balance


# Async loop implemented via threads
#----------------------------------------------


def runner():

    global pause
    global kill
    global running
    global DELAY
    global loop_count
    while(True):
        if not pause:
            # perform actions
            loop_count += 1
        if kill:
            running = False
            kill = False
            loop_count = 0
            break
        time.sleep(DELAY)


# Web3 and smart contract functions
#----------------------------------------------


def connect_web3(_provider=None):

    global global_provider
    global web3
    global web3_count
    if _provider:
        provider = _provider
    else:
        provider = global_provider
    if re.match(r'^https*:', provider):
        web3_provider = Web3.HTTPProvider(provider, request_kwargs={"timeout": 60})
    elif re.match(r'^ws*:', provider):
        web3_provider = Web3.WebsocketProvider(provider)
    elif re.match(r'^/', provider):
        web3_provider = Web3.IPCProvider(provider)
    else:
        raise RuntimeError("Unknown provider type " + provider)
    web3 = Web3(web3_provider)
    if not web3.isConnected():
        raise RuntimeError("Unable to connect to provider at " + provider)
    web3_count += 1
    global_provider = provider


def get_transactions(from_block, to_block, sender=None, recipient=None, topics=[]):

    _check_web3()
    global web3_count
    # query over block range
    # stop on failure
    # write results to json file
    return f'get_transactions() from: {from_block} to: {to_block}\n Global web3 count: {web3_count}'


def _get_token_balance(token, account):

    #print(f'In _get_token_balance with params: {token}, {account}')
    _check_web3()
    assert web3.isAddress(token) and web3.isAddress(account), 'Token and account must be addresses'
    token_contract = _get_contract(web3.toChecksumAddress(token), erc20_abi)
    return token_contract.functions.balanceOf(web3.toChecksumAddress(account)).call()


def _select_contract(contract):

    _check_web3()
    if contract == 'masterchef':
        return _get_contract(MASTERCHEF_ADDRESS, masterchef_abi)
    elif contract == 'factory_v1':
        return _get_contract(FACTORY_ADDRESS_V1, factory_abi)
    elif contract == 'router_v1':
        return _get_contract(ROUTER_ADDRESS_V1, router_abi)
    elif contract == 'factory_v2':
        return _get_contract(FACTORY_ADDRESS_V2, factory_abi)
    elif contract == 'router_v2':
        return _get_contract(ROUTER_ADDRESS_V2, router_abi)
    elif web3.isAddress(contract):
        address = web3.toChecksumAddress(contract)
        if address in pairs:
            abi = pair_abi
        if address in tokens:
            abi = erc20_abi
        return _get_contract(address, abi)
    return 'Specified contract not found'


def _check_web3():

    #print(f'In _check_web3')
    if not web3:
        connect_web3()
    if not web3.isConnected():
        connect_web3()


def _get_contract(contract_address, contract_abi):

    # assumes web3 has already been checked
    #print(f'In _get_contract with params: {contract_address}, {contract_abi}')
    return web3.eth.contract(address=contract_address, abi=contract_abi)
