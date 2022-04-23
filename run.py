from flask import Blueprint, jsonify, request
bp = Blueprint("run", __name__)
import json
import requests
from web3 import Web3, HTTPProvider
from web3.contract import ConciseContract
from pathlib import Path
import requests
import os
from PIL import Image
import base64
import io
from io import BytesIO

PINATA_BASE_URL = "https://api.pinata.cloud/"
endpoint = "pinning/pinJSONToIPFS"


api_key= os.environ["API_KEY"]
api_secret= os.environ["API_SECRET"]
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


headers_pinata = {
    "pinata_api_key": api_key,
    "pinata_secret_api_key": api_secret
}




@bp.route("/mint/",methods = ["GET", "POST"])
def mint():
    a= request.json['a']

    image = base64.b64decode(str(request.json['image']))

    imagePath = ("nft.png")
    img = Image.open(io.BytesIO(image))
    img.save(imagePath, 'png')
    
    headers = {
    'accept': 'application/json',
    'Content-Type': 'multipart/form-data',
    }

    files = {
    'image_file': ('nft.png', open('nft.png', 'rb'), 'image/png')
    }
    response = requests.post('https://imageserver.link/upload/image/file', files=files)
    url= response.json()['data']['image_url']
    print(url)
    x = {
    "name": "Snap Mint",
    "description": "Mint your snaps",
    "image": url
    }
    response_pinata = requests.post(
    PINATA_BASE_URL + endpoint,
    x,
    headers=headers_pinata,
    )

    print(response_pinata.json()['IpfsHash'])
    uri= "https://ipfs.io/ipfs/" + response_pinata.json()['IpfsHash']


    gas= requests.get("https://gasstation-mainnet.matic.network")
    gas= gas.json()["safeLow"]
    construct_txn = contract.functions.mint(a, uri).buildTransaction({
        'from': acct.address,
        'nonce': w3.eth.getTransactionCount(acct.address),
        'gas': 2558615,
        'gasPrice': w3.toWei(gas, 'gwei')})

    signed = acct.signTransaction(construct_txn)

    tx_hash=w3.eth.sendRawTransaction(signed.rawTransaction)
    print(tx_hash.hex())
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print(tx_receipt)
    nft = nft_Event.processReceipt(tx_receipt)[0]['args']['_tokenid']
    return jsonify({"status": 'success',"data":nft, "url": response.json()['data']['image_url']})


@bp.route("/URI/",methods = ["GET"])
def uri():
    tokenID= request.json['tokenid']
    uri= contract.functions.tokenURI(int(tokenID)).call()
    url= requests.get(uri).json()['image']
    return jsonify({"status": 'success',"data": url})

@bp.route("/owner/",methods = ["GET"])
def owner():
    tokenID= request.json['tokenid']
    uri= contract.functions.ownerOf(int(tokenID)).call()
    return jsonify({"status": 'success',"data": uri})

@bp.route("/balance/",methods = ["GET"])
def nums():
    address= request.json['address']
    uri= contract.functions.balanceOf(address).call()
    return jsonify({"status": 'success',"data": uri})