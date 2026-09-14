# TryHackMe – Mr. Phisher
### Room Link: https://tryhackme.com/room/mrphisher
## 1. Challenge Overview

**Platform:** TryHackMe
**Room:** Mr. Phisher
**Category:** Malware Analysis / Phishing / Office Macro Analysis
**Difficulty:** Beginner-friendly
**Main Concepts:**

* Phishing
* Malicious Office Documents
* VBA Macros
* Static Analysis
* XOR Encoding
* Python-based Decoding

---

## 2. Objective

Analyze a suspicious Microsoft Word macro-enabled document (`.docm`) without executing the macro, understand how the embedded VBA code hides information, decode the hidden data, and retrieve the flag.

---

## 3. Initial Reconnaissance

### Navigate to the challenge directory

```bash
cd /home/ubuntu/mrphisher
```

### List the available files

```bash
ls -lah
```

Expected files:

```text
MrPhisher.docm
mr-phisher.zip
```

### Identify the file types

```bash
file *
```

Expected result:

```text
MrPhisher.docm: Microsoft Word 2007+
mr-phisher.zip: Zip archive data, at least v2.0 to extract
```

### Confirm the files

```bash
find . -type f -maxdepth 2 -print
```

---

## 4. Identify the Suspicious File

The main file of interest is:

```text
MrPhisher.docm
```

The `.docm` extension indicates a **Microsoft Word Macro-Enabled Document**.

The challenge specifically warns about the document asking the user to enable macros.

### Security consideration

**Do not enable or execute the macros.**

Instead, inspect the VBA code statically.

---

## 5. Analyze the VBA Macro

Open `MrPhisher.docm` in LibreOffice and inspect the document's macros.

The discovered macro was:

```vb
Sub Format()
Dim a()
Dim b As String
a = Array(102, 109, 99, 100, 127, 100, 53, 62, 105, 57, 61, 106, 62, 62, 55, 110, 113, 114, 118, 39, 36, 118, 47, 35, 32, 125, 34, 46, 46, 124, 43, 124, 25, 71, 26, 71, 21, 88)
For i = 0 To UBound(a)
b = b & Chr(a(i) Xor i)
Next
End Sub
```

---

## 6. Understand the Macro

The macro contains an array of decimal numbers:

```vb
a = Array(102, 109, 99, 100, ...)
```

The important operation is:

```vb
Chr(a(i) Xor i)
```

This tells us that every value in the array is XORed with its index.

The resulting number is then converted into a character using `Chr()`.

### Decoding formula

```text
Decoded Character = Chr(Array Value XOR Index)
```

The decoded characters are concatenated into the variable:

```vb
b
```

---

## 7. Reproduce the Decoding with Python

Instead of executing the VBA macro, reproduce its logic safely using Python.

Run:

```bash
python3 -c 'a=[102,109,99,100,127,100,53,62,105,57,61,106,62,62,55,110,113,114,118,39,36,118,47,35,32,125,34,46,46,124,43,124,25,71,26,71,21,88]; print("".join(chr(x^i) for i,x in enumerate(a)))'
```

### What the Python code does

```python
enumerate(a)
```

provides:

```text
index → value
```

Then:

```python
x ^ i
```

performs the XOR operation.

Finally:

```python
chr(x ^ i)
```

converts the resulting number into a character.

The characters are joined together with:

```python
"".join(...)
```

---

## 8. Extracted Flag

The decoded output was:

```text
flag{a39a07a239aacd40c948d852a5c9f8d1}
```

### Flag

**`flag{a39a07a239aacd40c948d852a5c9f8d1}`**

---

## 9. Attack / Analysis Flow

```text
Suspicious Email
       │
       ▼
Macro-enabled Word Document
       │
       ▼
MrPhisher.docm
       │
       ▼
Static VBA Analysis
       │
       ▼
Integer Array
       │
       ▼
XOR with Array Index
       │
       ▼
Chr() Character Conversion
       │
       ▼
Decoded String
       │
       ▼
Flag
```

---

## 10. Tools Used

| Tool        | Purpose                    |
| ----------- | -------------------------- |
| `ls`        | List challenge files       |
| `file`      | Identify file types        |
| `find`      | Locate files               |
| LibreOffice | Inspect embedded VBA       |
| Python 3    | Reproduce the XOR decoding |
| VBA         | Understand macro logic     |

---

## 11. Key Learning Points

### What are macros?

Macros are small programs embedded in applications such as Microsoft Office. They can automate tasks, but attackers can abuse them to execute malicious commands.

### Why are `.docm` files interesting?

`.docm` files support embedded VBA macros. A document received through phishing may use a macro to execute malicious code when a victim enables macros.

### What is XOR?

XOR is a bitwise logical operation commonly represented by:

```text
^
```

In this challenge, each encoded value is XORed with its position/index:

```text
encoded_value XOR index
```

### Why use static analysis?

Static analysis allows us to examine potentially malicious code **without executing it**, reducing the risk of triggering malicious behavior.

---

## 12. Skills Practiced

* Phishing analysis
* Office document analysis
* VBA macro analysis
* Static malware analysis
* XOR decoding
* Python scripting
* Basic reverse engineering
* Safe handling of suspicious files

---