# TryHackMe — PassCode
### Room Link: https://tryhackme.com/room/hfb1passcode/
## 1. Challenge Overview

### Challenge Name

**PassCode**

### Category

* Web3 / Blockchain
* Smart Contract Security
* Ethereum
* Storage Analysis

### Scenario

The challenge involves the **DarkInject blockchain**. The objective is to identify a vulnerability or weakness in the deployed smart contract and manipulate its state so that the `isSolved()` function returns `true`.

### Objective

```text
Make isSolved() return true
```

Once the challenge is solved, retrieve the flag using the available `Get Flag` functionality.

---

# 2. Initial Challenge Information

The TryHackMe room provides a blockchain lab environment.

Expected lab machine:

```text
10.49.143.25
```

Important endpoints:

```text
RPC URL:
http://10.49.143.25:8545

API URL:
http://10.49.143.25
```

Expected blockchain information:

```text
Chain ID:
31337
```

The challenge also provides a player wallet containing test ETH.

---

# 3. Initial Setup

Start the TryHackMe lab machine and wait until the machine is fully initialized.

Set the environment variables:

```bash
export RPC_URL=http://10.49.143.25:8545
export API_URL=http://10.49.143.25
```

Retrieve the challenge information from the API:

```bash
curl -s "$API_URL/challenge" | jq
```

Extract the player wallet information:

```bash
export PRIVATE_KEY=$(curl -s "$API_URL/challenge" | jq -r ".player_wallet.private_key")
export PLAYER_ADDRESS=$(curl -s "$API_URL/challenge" | jq -r ".player_wallet.address")
export CONTRACT_ADDRESS=$(curl -s "$API_URL/challenge" | jq -r ".contract_address")
```

Verify the values:

```bash
echo "Player Address: $PLAYER_ADDRESS"
echo "Contract Address: $CONTRACT_ADDRESS"
```

---

# 4. Verify Blockchain Connectivity

Before attempting exploitation, confirm that the RPC endpoint is reachable.

Use the Ethereum JSON-RPC API:

```bash
curl -s -X POST "$RPC_URL" \
  -H "Content-Type: application/json" \
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_chainId",
    "params":[],
    "id":1
  }' | jq
```

Expected chain ID:

```text
31337
```

Also check the player's balance:

```bash
curl -s -X POST "$RPC_URL" \
  -H "Content-Type: application/json" \
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_getBalance",
    "params":["'"$PLAYER_ADDRESS"'","latest"],
    "id":1
  }' | jq
```

---

# 5. Identify the Smart Contract

The challenge provides a deployed contract address.

The first investigation should focus on understanding:

* Contract functions
* Function parameters
* State variables
* Access controls
* Constructor parameters
* Conditions required to solve the challenge
* Possible vulnerabilities
* Blockchain storage layout

Retrieve the deployed bytecode:

```bash
curl -s -X POST "$RPC_URL" \
  -H "Content-Type: application/json" \
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_getCode",
    "params":["'"$CONTRACT_ADDRESS"'","latest"],
    "id":1
  }' | jq
```

The result should contain the contract bytecode.

---

# 6. Obtain and Analyze the Contract Source

Check the challenge webpage for exposed Solidity source code.

If source code is available, document:

```text
Contract name
Compiler version
State variables
Constructor
Public functions
External functions
View functions
State-changing functions
Require conditions
Access-control checks
```

Pay particular attention to variables declared as:

```solidity
private
```

or:

```solidity
internal
```

because visibility modifiers do not necessarily prevent their underlying blockchain storage from being inspected.

---

# 7. Understand the Solve Condition

Determine exactly what `isSolved()` checks.

For example:

```solidity
function isSolved() external view returns (bool) {
    return unlock_flag;
}
```

If the function returns a state variable, identify:

1. Where that variable is initialized.
2. Which function modifies it.
3. What condition must be satisfied before it changes.
4. Whether that condition can be bypassed.
5. Whether the required value is stored on-chain.

The primary objective is to identify the state transition:

```text
isSolved() = false
        |
        v
Required contract state change
        |
        v
isSolved() = true
```

---

# 8. Investigate the Unlock Mechanism

If the contract contains a function similar to:

```solidity
function unlock(uint256 input) external returns (bool) {
    if (input == code) {
        unlock_flag = true;
        return true;
    }

    return false;
}
```

then determine how the value of:

```solidity
code
```

can be obtained.

Questions to answer:

* Is `code` supplied to the constructor?
* Is `code` stored on-chain?
* Is `code` exposed through a public getter?
* Is `code` marked `private`?
* Can the corresponding storage slot be read through the RPC?
* Can the required value be recovered without guessing?

---

# 9. Determine the Solidity Storage Layout

If the source code shows state variables such as:

```solidity
string private secret;
bool private unlock_flag;
uint256 private code;
string private hint_text;
```

map the variables to their storage locations.

For simple fixed-size variables, the expected layout can be investigated by examining consecutive storage slots.

Do not assume the slot without verification.

Potential investigation:

```text
Slot 0 → investigate
Slot 1 → investigate
Slot 2 → investigate
Slot 3 → investigate
```

---

# 10. Read Contract Storage

Ethereum JSON-RPC provides:

```text
eth_getStorageAt
```

which can be used to inspect a contract's storage.

Generic command:

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

If a potentially interesting value is found, document:

```text
Storage slot:
Raw hexadecimal value:
Expected variable:
Decoded value:
```

---

# 11. Decode Any Recovered Value

If a storage slot contains a numeric value, convert it from hexadecimal to decimal.

Example:

```bash
python3 -c "print(int('0xVALUE', 16))"
```

Do not send a transaction until the recovered value has been validated against the contract logic.

---

# 12. Plan the Transaction

Once the required input is known, construct the transaction for the relevant state-changing function.

Example:

```text
unlock(<recovered_code>)
```

The transaction must be sent from the player wallet.

Required information:

```text
RPC URL
Chain ID
Contract address
Player private key
Player address
Function name
Function parameters
Nonce
Gas configuration
```

---

# 13. Transaction Execution

If Foundry is available, `cast` can be used.

Check:

```bash
which cast
```

If it is unavailable, use an alternative such as `web3.py`.

Install Web3 if required:

```bash
pip3 install web3
```

The transaction should only be executed after the contract state and required input have been confirmed.

---

# 14. Verify the Exploitation Result

After sending the transaction, verify the transaction status.

Then call:

```text
isSolved()
```

The expected state transition is:

```text
false
  ↓
successful transaction
  ↓
true
```

If `isSolved()` remains `false`, investigate:

* Incorrect storage slot
* Incorrect decoded value
* Wrong contract address
* Wrong chain/RPC
* Failed transaction
* Incorrect player wallet
* Incorrect function parameters

---

# 15. Retrieve the Flag

Once:

```text
isSolved() = true
```

call the contract's flag function if available:

```text
getFlag()
```

Alternatively, use the **Get Flag** button provided by the challenge webpage.

Do not attempt to retrieve the flag before satisfying the contract's solve condition.

---

# 16. Evidence to Record

For the final write-up, capture the following evidence:

### Initial State

```text
Contract address:
Player address:
RPC:
Chain ID:
Initial isSolved() result:
```

### Contract Analysis

```text
Relevant state variable:
Relevant function:
Required condition:
```

### Storage Analysis

```text
Storage slot:
Raw storage value:
Decoded value:
```

### Exploitation

```text
Function called:
Transaction hash:
Transaction status:
```

### Final Verification

```text
isSolved():
Flag:
```

---

# 17. Investigation Workflow

The complete planned workflow is:

```text
Start Lab
   |
   v
Obtain challenge information
   |
   v
Configure RPC / wallet / contract variables
   |
   v
Verify blockchain connectivity
   |
   v
Inspect contract source / bytecode
   |
   v
Understand isSolved()
   |
   v
Identify state variable controlling the solution
   |
   v
Analyze the function that modifies the state
   |
   v
Determine required input
   |
   v
Analyze Solidity storage layout
   |
   v
Read relevant storage through eth_getStorageAt
   |
   v
Decode recovered value
   |
   v
Construct state-changing transaction
   |
   v
Send transaction using player wallet
   |
   v
Verify isSolved() == true
   |
   v
Retrieve flag
```

---

# 18. Key Concepts to Learn

This room should reinforce the following Web3 security concepts:

* Ethereum JSON-RPC
* Smart contract interaction
* Solidity state variables
* Solidity visibility modifiers
* Contract storage
* Storage slots
* `eth_getStorageAt`
* Function calls vs. transactions
* Transaction signing
* Ethereum chain IDs
* Wallet private keys
* Smart contract state manipulation

## Important Security Lesson

A Solidity declaration such as:

```solidity
uint256 private code;
```

should **not** be treated as cryptographically secret.

The `private` modifier controls Solidity-level access from other contracts. It does not encrypt the value or remove it from the public blockchain state.

Therefore, during the investigation, any sensitive-looking state variable should be evaluated from the perspective of what can actually be observed from blockchain storage.