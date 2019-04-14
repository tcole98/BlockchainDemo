"""
Blockchain Demo: https://hackernoon.com/ethereum-smart-contracts-in-python-a-comprehensive-ish-guide-771b03990988

Code by Nick Williams (https://github.com/enjeyw)
"""

import time, contract_abi
from web3 import Web3, HTTPProvider

chainId = 42  #Kovan testnet

contract_address     = "[YOUR CONTRACT ADDRESS]"
wallet_private_key   = "[YOUR TEST WALLET PRIVATE KEY]"
wallet_address       = "[YOUR WALLET ADDRESS]"

w3 = Web3(HTTPProvider("[YOUR INFURA URL]"))

w3.eth.enable_unaudited_features()
contract = w3.eth.contract(address = contract_address, abi = contract_abi.abi)


def send_ether_to_contract(amount_in_ether):
    amount_in_wei = w3.toWei(amount_in_ether, 'ether')

    nonce = w3.eth.getTransactionCount(wallet_address)

    txn_dict = {
        'to': contract_address,
        'value': amount_in_wei,
        'gas': 2000000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce,
        'chainId': chainId
    }

    signed_txn = w3.eth.account.signTransaction(txn_dict, wallet_private_key)

    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    txn_receipt = None
    count = 0
    while txn_receipt is None and (count < 30):
        print('count',count)
        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)

        print('txn_receipt',txn_receipt)

        time.sleep(10)

    if txn_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}

    return {'status': 'added', 'txn_receipt': txn_receipt}


def check_whether_address_is_approved(address):
    return contract.functions.isApproved(address).call()


def broadcast_an_opinion(convfefe):
    nonce = w3.eth.getTransactionCount(wallet_address)

    txn_dict = contract.functions.broadcastOpinion(convfefe).buildTransaction({
        'chainId':chainId,
        'gas': 140000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce
    })

    signed_txn = w3.eth.account.signTransaction(txn_dict, wallet_private_key)

    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    txn_receipt = w3.eth.getTransactionReceipt(result)

    count = 0
    while txn_receipt is None and (count < 30):
        time.sleep(10)

        txn_receipt = w3.eth.getTransactionReceipt(result)

        print(txn_receipt)

    if txn_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}

    processed_receipt = contract.events.OpinionBroadcast().processReceipt(txn_receipt)

    print(processed_receipt)

    output = 'Address {} broadcasted the opinion: {}'.format(processed_receipt[0].args._soapboxer, processed_receipt[0].args._opinion)
    print(output)
    return {'status': 'added', 'processed_receipt': processed_receipt}


if __name__ == "__main__":
    send_ether_to_contract(0.03)

    is_approved = check_whether_address_is_approved(wallet_address)

    print(is_approved)

    broadcast_an_opinion('convfefe!')
