import json
from web3 import Web3

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
print("Connected to Ganache:", w3.is_connected())

# Get the first Ganache account
account = w3.eth.accounts[0]

# We are pre-compiling the bytecode so you don't need Remix!
# This is the exact bytecode for your CampusConnectLedger contract.
bytecode = "0x6080604052348015600e575f5ffd5b506101978061001c5f395ff3fe608060405234801561000f575f5ffd5b5060043610610034575f3560e01c80634e8fee0014610038578063a21f3c6a14610068575b5f5ffd5b610052600480360381019061004d91906100f0565b610084565b60405161005f9190610148565b60405180910390f35b610082600480360381019061007d91906100f0565b6100a0565b005b5f815f5f8581526020019081526020015f205414905092915050565b805f5f8481526020019081526020015f20819055505050565b5f5ffd5b5f819050919050565b6100cf816100bd565b81146100d9575f5ffd5b50565b5f813590506100ea816100c6565b92915050565b5f5f60408385031215610106576101056100b9565b5b5f610113858286016100dc565b9250506020610124858286016100dc565b9150509250929050565b5f8115159050919050565b6101428161012e565b82525050565b5f60208201905061015b5f830184610139565b9291505056fea2646970667358221220bc2fcb8f0d7f3b307f44e62183ebca24aba12eba286337781b1f48750f62029364736f6c63430008220033"

# The ABI tells Python how to talk to the contract
abi = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "refId", "type": "bytes32"},
            {"internalType": "bytes32", "name": "contentHash", "type": "bytes32"}
        ],
        "name": "anchor",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "refId", "type": "bytes32"},
            {"internalType": "bytes32", "name": "contentHash", "type": "bytes32"}
        ],
        "name": "verify",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Deploy the contract
Ledger = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = Ledger.constructor().transact({'from': account})
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"✅ Contract deployed successfully!")
print(f"Contract Address: {tx_receipt.contractAddress}")