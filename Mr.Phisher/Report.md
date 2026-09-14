# Mr. Phisher — Report

## 1. Executive Summary

The **Mr. Phisher** challenge on TryHackMe involved analyzing a suspicious phishing attachment in the form of a Microsoft Word macro-enabled document.

The objective was to investigate the embedded VBA macro without executing it, understand its obfuscation technique, and recover the hidden flag.

The macro contained an array of integer values and used an **XOR operation with the array index** to decode the values into characters.

---

## 2. Challenge Information

| Field                | Details                                                 |
| -------------------- | ------------------------------------------------------- |
| Platform             | TryHackMe                                               |
| Challenge            | Mr. Phisher                                             |
| Primary Category     | Malware Analysis                                        |
| Secondary Categories | Phishing, VBA Macro Analysis, Static Analysis, Encoding |
| Target File          | `MrPhisher.docm`                                        |
| Analysis Environment | TryHackMe Ubuntu VM                                     |
| Result               | Flag successfully recovered                             |

---

## 3. Objective

The objectives of the investigation were:

1. Identify the suspicious attachment.
2. Determine the file type.
3. Analyze the embedded VBA macro.
4. Identify the data-obfuscation technique.
5. Decode the hidden information.
6. Recover the challenge flag.

---

## 4. Initial File Enumeration

The challenge files were located at:

```text
/home/ubuntu/mrphisher
```

The directory was accessed using:

```bash
cd /home/ubuntu/mrphisher
```

The contents were enumerated:

```bash
ls -lah
```

The following files were discovered:

```text
MrPhisher.docm
mr-phisher.zip
```

The file types were then identified:

```bash
file *
```

The results identified:

```text
MrPhisher.docm: Microsoft Word 2007+
mr-phisher.zip: Zip archive data, at least v2.0 to extract
```

The `.docm` file was identified as the primary target because the challenge specifically referenced a document requesting the user to enable macros.

---

## 5. VBA Macro Analysis

The document was opened in **LibreOffice** and its embedded macros were inspected.

The following VBA macro was identified:

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

The macro was **not executed** during the investigation.

---

## 6. Analysis of the Macro

The macro contains an array of decimal values:

```vb
a = Array(102, 109, 99, 100, ...)
```

The main decoding operation is:

```vb
Chr(a(i) Xor i)
```

This performs two operations:

1. XOR the array value with its index.
2. Convert the resulting number into a character using `Chr()`.

Conceptually:

```text
Decoded Character = Chr(Encoded Value XOR Index)
```

The decoded characters are appended to the string variable `b`:

```vb
b = b & Chr(a(i) Xor i)
```

This indicates that the integer array is an obfuscated representation of the final string.

---

## 7. Python-Based Decoding

The VBA decoding logic was reproduced using Python instead of executing the macro.

The following command was used:

```bash
python3 -c 'a=[102,109,99,100,127,100,53,62,105,57,61,106,62,62,55,110,113,114,118,39,36,118,47,35,32,125,34,46,46,124,43,124,25,71,26,71,21,88]; print("".join(chr(x^i) for i,x in enumerate(a)))'
```

The Python implementation performs the same operation as the VBA code:

```text
Array Value → XOR with Index → Convert to Character → Concatenate
```

---

## 8. Result

The decoding operation produced:

```text
flag{a39a07a239aacd40c948d852a5c9f8d1}
```

### Recovered Flag

```text
flag{a39a07a239aacd40c948d852a5c9f8d1}
```

---

## 9. Attack / Analysis Chain

```text
Suspicious Phishing Email
        ↓
Macro-Enabled Word Document
        ↓
MrPhisher.docm
        ↓
VBA Macro Inspection
        ↓
Integer Array Identified
        ↓
XOR Operation Identified
        ↓
Array Values XORed With Their Index
        ↓
Chr() Conversion
        ↓
Hidden String Recovered
        ↓
Flag
```

---

## 10. Security Relevance

This challenge demonstrates how attackers can use **Office macros in phishing attachments** to hide malicious functionality or data.

A macro-enabled document should be treated with caution when received from an untrusted source, especially when the document instructs the user to enable macros.

The investigation also demonstrates the importance of **static analysis**. The embedded VBA could be analyzed without executing it, allowing the encoded information to be recovered safely.

---

## 11. Key Indicators and Techniques

### File Indicator

```text
MrPhisher.docm
```

### Macro Indicator

```vb
Sub Format()
```

### Obfuscated Data

```vb
Array(102, 109, 99, 100, 127, ...)
```

### Decoding Operation

```vb
a(i) Xor i
```

### Character Conversion

```vb
Chr(...)
```

### Final Flag

```text
flag{a39a07a239aacd40c948d852a5c9f8d1}
```

---

## 12. Tools Used

* TryHackMe Ubuntu VM
* Linux Terminal
* `ls`
* `file`
* `find`
* LibreOffice
* VBA Macro Editor
* Python 3

---

## 13. Skills Demonstrated

* Phishing attachment analysis
* Microsoft Office document analysis
* VBA macro analysis
* Static malware analysis
* XOR decoding
* Python scripting
* Basic reverse engineering
* Safe analysis of potentially malicious documents

---

## 14. Conclusion

The **Mr. Phisher** challenge demonstrated a simple example of malicious or suspicious Office macro analysis.

The investigation began by identifying the macro-enabled `.docm` attachment. The embedded VBA code was then inspected statically. The macro was found to contain an integer array whose values were XORed with their corresponding indexes and converted into characters using `Chr()`.

By reproducing this logic in Python, the hidden flag was successfully recovered without executing the macro.

**Final Flag:**

```text
flag{a39a07a239aacd40c948d852a5c9f8d1}
```