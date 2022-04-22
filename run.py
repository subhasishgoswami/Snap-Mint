from flask import Blueprint, jsonify, request
bp = Blueprint("run", __name__)

import json
import requests
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract

import os

user = os.environ['USER']

# web3.py instance
w3 = Web3(HTTPProvider('https://polygon-rpc.com'))
print(w3.isConnected())

key= user
acct = w3.eth.account.privateKeyToAccount(key)

# compile your smart contract with truffle first
truffleFile = json.load(open('./build/contracts/NFT.json'))
abi = truffleFile['abi']
address= "0x1D17a42834dD63A410a0a55d73cc7d6413C69fFe"
contract= w3.eth.contract(address= address, abi=abi)
nft_Event = contract.events.nft()

headers = {
    'accept': 'application/json',
    'Content-Type': 'multipart/form-data',
}
files = {
    'image_file': ('ipfs.png', open('ipfs.png', 'rb'), 'image/png')
}

@bp.route("/", methods= ["GET"])
def landing():
    return jsonify({"status": 'success',"data":"nft"})
@bp.route("/mint/",methods = ["GET", "POST"])
def mint():
    a= request.json['a']
    response = requests.post('https://imageserver.link/upload/image/file', files=files)
    print(response.json()['data']['image_url'])
    construct_txn = contract.functions.mint(a, response.json()['data']['image_url']).buildTransaction({
        'from': acct.address,
        'nonce': w3.eth.getTransactionCount(acct.address),
        'gas': 2558615,
        'gasPrice': w3.toWei('40', 'gwei')})

    signed = acct.signTransaction(construct_txn)

    tx_hash=w3.eth.sendRawTransaction(signed.rawTransaction)
    print(tx_hash.hex())
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print(tx_receipt)
    nft = nft_Event.processReceipt(tx_receipt)[0]['args']['_tokenid']
    return jsonify({"status": 'success',"data":nft, "url": response.json()['data']['image_url']})