from web3 import Web3
import re
import json
import time
from threading import Thread
import asyncio
import lib.abis as abis

# global variables
web3 = None
global_provider = 'https://bsc-dataseed.binance.org/'
web3_count = 0
pause = False
kill = False
running = False
DELAY = 1 # in seconds

# for testing
loop_count = 0

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

# Functions for basic command routes
#----------------------------------------------

def get_status():
    global loop_count
    return f'Total loop count: {loop_count}'

def start_process():
    global running
    if not running:
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

# Async functions implemented via threads
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

    if not web3:
        connect_web3()
    if not web3.isConnected():
        connect_web3()
    global web3_count
    # query over block range
    # stop on failure
    # write results to json file
    return f'get_transactions() from: {from_block} to: {to_block}\n Global web3 count: {web3_count}'

def _select_contract(contract):
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

def _get_contract(contract_address, contract_abi):
    if not web3:
        connect_web3()
    if not web3.isConnected():
        connect_web3()
    return web3.eth.contract(address=contract_address, abi=contract_abi)
