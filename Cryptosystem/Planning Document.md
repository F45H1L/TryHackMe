# Cryptosystem – Planning Document
## Room Link - https://tryhackme.com/room/hfb1cryptosystem
## 1. Objective

Analyze the recovered Python source code and RSA parameters to identify a weakness in the key-generation process and recover the secret flag.

## 2. Challenge Information

* **Platform:** TryHackMe
* **Challenge:** Cryptosystem
* **Category:** Cryptography
* **Technique:** RSA Cryptanalysis
* **Primary Attack:** Fermat Factorization

## 3. Initial Analysis

Review the provided Python code and identify how the RSA keys are generated.

Important observation:

```python
p = getPrime(1024)
q = primo(p)
```

The function `primo()` generates the next prime after `p`. Therefore, `p` and `q` are extremely close.

## 4. Attack Plan

1. Extract the RSA values:

   * `n`
   * `e`
   * `c`

2. Analyze the relationship between `p` and `q`.

3. Use **Fermat factorization** to factor `n` into:

   * `p`
   * `q`

4. Calculate Euler's totient:

```text
φ(n) = (p - 1)(q - 1)
```

5. Calculate the private exponent:

```text
d = e⁻¹ mod φ(n)
```

6. Decrypt the ciphertext:

```text
m = cᵈ mod n
```

7. Convert the resulting integer into readable text.

8. Verify the recovered flag.

## 5. Tools Required

* Kali Linux / TryHackMe AttackBox
* Python 3
* Python `math.isqrt`
* PyCryptodome

## 6. Expected Outcome

Successfully factor the RSA modulus, calculate the private key, decrypt the ciphertext, and recover the secret flag.

## 7. Success Criteria

The challenge is considered complete when:

* `p` and `q` are successfully recovered.
* The RSA private exponent `d` is calculated.
* The ciphertext is decrypted.
* A valid TryHackMe flag is obtained.
