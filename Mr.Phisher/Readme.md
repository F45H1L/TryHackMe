## 1. Access the challenge machine

Started the TryHackMe machine and opened the terminal.

## 2. Navigate to the challenge directory
```bash
cd /home/ubuntu/mrphisher
```
## 3. List the available files
```bash
ls -lah
```
This revealed:

MrPhisher.docm
mr-phisher.zip

## 4. Identify the file types

file *

Output showed:

MrPhisher.docm: Microsoft Word 2007+
mr-phisher.zip: Zip archive data, at least v2.0 to extract

The .docm extension indicated a Microsoft Word macro-enabled document.

## 5. Locate the challenge files
```bash
find . -type f -maxdepth 2 -print
```
This confirmed the two files in the directory:

./MrPhisher.docm
./mr-phisher.zip

## 6. Inspect the Word document

Open MrPhisher.docm in LibreOffice and navigate to the document's macros.

The following is the VBA macro:
```
Sub Format()
Dim a()
Dim b As String
a = Array(102, 109, 99, 100, 127, 100, 53, 62, 105, 57, 61, 106, 62, 62, 55, 110, 113, 114, 118, 39, 36, 118, 47, 35, 32, 125, 34, 46, 46, 124, 43, 124, 25, 71, 26, 71, 21, 88)
For i = 0 To UBound(a)
b = b & Chr(a(i) Xor i)
Next
End Sub
```
7. Identify the decoding technique

The important line is:

b = b & Chr(a(i) Xor i)

This means every value in the array is:

XORed with its array index i
Converted into a character using Chr()
Added to the string b

So the decoding formula is:

character = Chr(array_value XOR index)

8. Reproduce the decoding in Python

Use:
```bash
python3 -c 'a=[102,109,99,100,127,100,53,62,105,57,61,106,62,62,55,110,113,114,118,39,36,118,47,35,32,125,34,46,46,124,43,124,25,71,26,71,21,88]; print("".join(chr(x^i) for i,x in enumerate(a)))'
```
9. Decode the flag

The command returns the Flag:
```bash
flag{a39a07a239aacd40c948d852a5c9f8d1}
```
Key takeaway: The malicious-looking macro was using a simple XOR cipher with the array index as the XOR key. No need to execute the macro; static analysis of the VBA was enough to recover the flag.