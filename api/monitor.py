import os
from web3 import Web3
from dotenv import load_dotenv
import time

# بارگذاری اطلاعات از فایل .env
load_dotenv()

# اطلاعات از فایل .env
sender_address = os.getenv('SENDER_ADDRESS')
receiver_address = os.getenv('RECEIVER_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')
infura_project_id = os.getenv('INFURA_PROJECT_ID')
token_address = os.getenv('TOKEN_CONTRACT_ADDRESS')

# اتصال به شبکه Ethereum با استفاده از Infura
w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{infura_project_id}"))

# ABI استاندارد ERC-20
token_abi = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

# اتصال به قرارداد توکن
token_contract = w3.eth.contract(address=token_address, abi=token_abi)

# تابع محاسبه گس برای ارسال توکن
def calculate_gas():
    tx = token_contract.functions.transfer(receiver_address, 0).buildTransaction({
        'from': sender_address,
        'gas': 200000,
        'gasPrice': w3.toWei('20', 'gwei'),
        'nonce': w3.eth.getTransactionCount(sender_address),
    })
    gas_estimate = w3.eth.estimateGas(tx)
    return gas_estimate

# بررسی موجودی کیف پول و ارسال توکن‌ها
def send_tokens():
    balance = token_contract.functions.balanceOf(sender_address).call()
    gas_needed = calculate_gas()
    
    if balance > gas_needed:
        amount_to_send = balance - gas_needed
        
        tx = token_contract.functions.transfer(receiver_address, amount_to_send).buildTransaction({
            'from': sender_address,
            'gas': 200000,
            'gasPrice': w3.toWei('20', 'gwei'),
            'nonce': w3.eth.getTransactionCount(sender_address),
        })
        
        signed_txn = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(f"Transaction sent: {tx_hash.hex()}")
    else:
        print("Not enough tokens or gas.")

# تابع برای نظارت و اجرای تراکنش
def monitor_transactions():
    while True:
        try:
            send_tokens()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(0.01)  # هر 0.01 ثانیه بررسی شود

# شروع نظارت
monitor_transactions()
