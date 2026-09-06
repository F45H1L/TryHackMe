# Cryptosystem – Security Testing Report

## 1. Executive Summary

The **Cryptosystem** challenge involved analyzing an RSA implementation and recovering a secret message from an intercepted ciphertext.

The RSA implementation contained a critical weakness in its prime-generation process. The value `q` was generated as the next prime after `p`, causing the two RSA primes to be extremely close.

This weakness allowed the RSA modulus to be factored using **Fermat Factorization**, after which the RSA private key was reconstructed and the ciphertext successfully decrypted.

**Result:** The secret flag was successfully recovered.

---

## 2. Scope

| Item          | Details                   |
| ------------- | ------------------------- |
| Platform      | TryHackMe                 |
| Challenge     | Cryptosystem              |
| Category      | Cryptography              |
| Algorithm     | RSA                       |
| Vulnerability | Weak RSA prime generation |
| Attack        | Fermat Factorization      |
| Status        | Successfully exploited    |

---

## 3. Source Code Analysis

The recovered source code contained the following RSA key-generation logic:

```python
p = getPrime(1024)
q = primo(p)
n = p * q
e = 0x10001
d = inverse(e, (p-1) * (q-1))
```

The `primo()` function generates the next prime after the supplied value:

```python
def primo(n):
    n += 2 if n & 1 else 1
    while not isPrime(n):
        n += 2
    return n
```

Therefore, `q` is the next prime following `p`.

This results in:

```text
p ≈ q
```

which is insecure for RSA.

---

## 4. Vulnerability Identification

Normal RSA security relies on the difficulty of factoring:

```text
n = p × q
```

where `p` and `q` should be independently generated large primes.

In this implementation, however:

```text
q = next_prime(p)
```

makes the primes extremely close.

The recovered factors were:

```text
p = 126318051608086363086436167670344263394080470820595614431601340322770842077281561270430546458181927047035107171495443733059446197321213039114058879074116435004275746677895184166416072439425851436685237749376105428613752816760479906270662609845420347955146870576553890171297646523338757410772905372711647921869

q = 126318051608086363086436167670344263394080470820595614431601340322770842077281561270430546458181927047035107171495443733059446197321213039114058879074116435004275746677895184166416072439425851436685237749376105428613752816760479906270662609845420347955146870576553890171297646523338757410772905372711647922039
```

The difference was only:

```text
q - p = 170
```

This confirmed that Fermat Factorization was suitable.

---

## 5. Exploitation Method

Fermat Factorization represents the modulus as:

```text
n = a² - b²
```

which can be rewritten as:

```text
n = (a-b)(a+b)
```

The attack started with:

```python
a = isqrt(n)

if a * a < n:
    a += 1
```

The value of `a` was incremented until:

```text
a² - n = b²
```

Once `b` was found:

```text
p = a - b
q = a + b
```

The RSA modulus was successfully factored.

---

## 6. Private Key Recovery

After recovering `p` and `q`, Euler's totient was calculated:

```text
φ(n) = (p - 1)(q - 1)
```

The private exponent was then calculated:

```text
d = e⁻¹ mod φ(n)
```

with:

```text
e = 65537
```

This successfully reconstructed the RSA private key component `d`.

---

## 7. Ciphertext Decryption

The intercepted ciphertext was decrypted using:

```text
m = cᵈ mod n
```

The resulting integer was converted into bytes and decoded as text.

---

## 8. Result

The recovered flag was:

```text
THM{Just_s0m3_small_amount_of_RSA!}
```

**Status: Successfully completed.**

---

## 9. Impact

If this implementation were used in a real-world application, an attacker could factor the RSA modulus and recover the private key.

Potential consequences include:

* Decryption of protected communications
* Recovery of confidential information
* Impersonation using the compromised private key
* Compromise of RSA-based authentication or signatures

---

## 10. Remediation

To prevent this vulnerability:

1. Generate `p` and `q` independently using a cryptographically secure random number generator.
2. Do not generate one RSA prime from another.
3. Use a well-tested cryptographic library for RSA key generation.
4. Ensure RSA primes are sufficiently large and independently generated.
5. Follow established cryptographic standards for key generation.

A secure approach should resemble:

```python
p = getPrime(1024)
q = getPrime(1024)
```

rather than:

```python
q = primo(p)
```

---

## 11. Conclusion

The challenge demonstrated how improper RSA key generation can completely undermine the security of otherwise strong cryptography.

Although RSA with sufficiently large keys is computationally difficult to factor under normal conditions, generating two extremely close primes made **Fermat Factorization** practical.

The vulnerability was successfully identified, exploited, and the encrypted flag was recovered.

**Final Flag:**

```text
THM{Just_s0m3_small_amount_of_RSA!}
```
