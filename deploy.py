from solcx import compile_standard, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv
import os
from pprint import pprint

load_dotenv()

OWNER_ADDRESS = os.getenv("OWNER_ADDRESS")
CHAIN_ID = int(os.getenv("CHAIN_ID"))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

with open("./SimpleStorage.sol") as contract:
    simple_storage_contract = contract.read()


# ** compile
compiling_contract = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_contract}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version=install_solc("0.6.0"),
)

with open("compiled_code.json", "w") as compiled_contract:
    json.dump(compiling_contract, compiled_contract)

bytecode = compiling_contract["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

abi = json.loads(
    compiling_contract["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# ** build the transaction
SimpleStorageContract = w3.eth.contract(abi=abi, bytecode=bytecode)

# ** get nonce
transaction_count = w3.eth.getTransactionCount(OWNER_ADDRESS)

# ** create new transaction
new_transaction = SimpleStorageContract.constructor().buildTransaction(
    {"chainId": CHAIN_ID, "from": OWNER_ADDRESS, "nonce": transaction_count}
)

# ** sign transaction with private key
signed_transaction = w3.eth.account.sign_transaction(new_transaction, PRIVATE_KEY)

# ** send transaction
transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)

# ** working with contract we deployed
deployed_contract = w3.eth.contract(
    address=transaction_receipt.contractAddress, abi=abi
)

print(deployed_contract.functions.retrieve().call())
store_transaction = deployed_contract.functions.store(69).buildTransaction(
    {
        "chainId": CHAIN_ID,
        "from": OWNER_ADDRESS,
        "nonce": transaction_count
        + 1,  # NOTE as we already used actual transaction_count before as nonce
    }
)  # ** well it is a sexiest number

# ** sign store transaction
signed_store_transaction = w3.eth.account.sign_transaction(
    store_transaction, PRIVATE_KEY
)
store_transaction_hash = w3.eth.send_raw_transaction(
    signed_store_transaction.rawTransaction
)
store_transaction_receipt = w3.eth.wait_for_transaction_receipt(store_transaction_hash)
print(deployed_contract.functions.retrieve().call())
