import os
import threading
from web3 import Web3
from dotenv import load_dotenv
import time

# بارگذاری اطلاعات از فایل .env
load_dotenv()

# اطلاعات از فایل .env
sender_address = os.getenv('SENDER_ADDRESS')
receiver_address = os.getenv('RECEIVER_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')
token_address = os.getenv('TOKEN_CONTRACT_ADDRESS')

# اطلاعات مربوط به شبکه‌ها از .env
networks = ['ethereum', 'polygon', 'bnb', 'base']

# تنظیم URLهای مختلف برای شبکه‌ها
network_urls = {
    'ethereum': f"https://mainnet.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}",
    'polygon': f"https://polygon-rpc.com",
    'bnb': f"https://bsc-dataseed.binance.org/",
    'base': f"https://base-rpc.org"  # باید RPC مناسب Base پیدا کنید
}

# ABI استاندارد ERC-20 (برای اکثر توکن‌ها)
token_abi = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# تابع برای محاسبه گس
def calculate_gas(w3, sender_address):
    tx = token_contract.functions.transfer(receiver_address, 0).buildTransaction({
        'from': sender_address,
        'gas': 200000,
        'gasPrice': w3.toWei('20', 'gwei'),
        'nonce': w3.eth.getTransactionCount(sender_address),
    })
    gas_estimate = w3.eth.estimateGas(tx)
    return gas_estimate

# تابع برای ارسال توکن
def send_tokens(w3, token_contract, sender_address, private_key, receiver_address):
    balance = token_contract.functions.balanceOf(sender_address).call()
    gas_needed = calculate_gas(w3, sender_address)
    
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
        print(f"Transaction sent on network {w3.provider.endpointUri}: {tx_hash.hex()}")
    else:
        print(f"Not enough tokens or gas on network {w3.provider.endpointUri}.")

# تابع برای نظارت و اجرای تراکنش‌ها برای هر شبکه
def monitor_network(network, w3):
    # اتصال به قرارداد توکن
    token_contract = w3.eth.contract(address=token_address, abi=token_abi)
    while True:
        try:
            send_tokens(w3, token_contract, sender_address, private_key, receiver_address)
        except Exception as e:
            print(f"Error on network {network}: {e}")
        time.sleep(0.01)  # هر 0.01 ثانیه بررسی شود

# تابع برای راه‌اندازی و اجرای همزمان تراکنش‌ها در تمام شبکه‌ها
def start_monitoring():
    threads = []
    
    for network in networks:
        # اتصال به هر شبکه
        w3 = Web3(Web3.HTTPProvider(network_urls.get(network)))
        
        # ایجاد thread برای هر شبکه
        thread = threading.Thread(target=monitor_network, args=(network, w3))
        threads.append(thread)
        thread.start()
    
    # منتظر ماندن برای اتمام تمام thread‌ها
    for thread in threads:
        thread.join()

# شروع نظارت
start_monitoring()