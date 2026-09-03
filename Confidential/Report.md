# TryHackMe — Confidential

## Security Testing / CTF Walkthrough Report

### 1. Executive Summary

The objective of the **Confidential** TryHackMe challenge was to recover a secret invite code contained within a QR code embedded in a PDF document. The QR code was obscured by an image within the PDF.

The investigation was performed on the TryHackMe AttackBox. The PDF was analyzed using `pdfimages`, the embedded images were extracted, and the extracted image containing the QR code was opened and scanned.

The QR code was successfully decoded, resulting in the challenge flag.

---

## 2. Objective

The primary objective of this assessment was to:

* Locate the confidential PDF.
* Identify images embedded within the PDF.
* Extract the embedded images.
* Locate the QR code.
* Decode the QR code.
* Obtain the challenge flag.

---

## 3. Scope

### Target

```text
/home/ubuntu/confidential/Repdf.pdf
```

### Environment

* TryHackMe AttackBox
* Linux
* Local challenge environment

### Tools Used

| Tool         | Purpose                              |
| ------------ | ------------------------------------ |
| `ls`         | Directory/file enumeration           |
| `pdfimages`  | PDF image enumeration and extraction |
| File Manager | Access extracted files               |
| Image Viewer | Inspect extracted images             |
| QR Scanner   | Decode the QR code                   |

---

# 4. Methodology

## 4.1 Navigate to the Challenge Directory

The first step was to navigate to the directory containing the challenge file:

```bash
cd /home/ubuntu/confidential
```

The directory was then enumerated using:

```bash
ls -la
```

The directory contained the following PDF:

```text
Repdf.pdf
```

---

## 4.2 Enumerate Images Within the PDF

The `pdfimages` utility was used to inspect the images embedded within the PDF:

```bash
pdfimages -list /home/ubuntu/confidential/Repdf.pdf
```

The command returned three image objects:

```text
page  num  type   width height color comp bpc enc   interp object ID x-ppi y-ppi size
-------------------------------------------------------------------------------------
1     0    image  850   1100  gray  1    8   image  yes    10  0     73    73    85.7K
1     1    image  187   169   rgb   3    8   image  yes    13  0     73    73    9060B
1     2    smask  187   169   gray  1    8   image  yes    13  0     73    73    3150B
```

### Observation

The output indicated that the PDF contained multiple image objects, including:

* An `850 × 1100` grayscale image.
* A `187 × 169` RGB image.
* A `187 × 169` grayscale soft mask (`smask`).

The presence of the RGB image and associated soft mask was particularly relevant because the challenge indicated that an image was covering the QR code.

---

## 4.3 Create an Extraction Directory

A dedicated directory was created to store the extracted PDF images:

```bash
mkdir pdf_extract
```

This ensured that the extracted files were kept separate from the original challenge file.

---

## 4.4 Extract Embedded Images

All embedded images were extracted using:

```bash
pdfimages -all /home/ubuntu/confidential/Repdf.pdf pdf_extract/image
```

The `-all` option was used to extract the available image data, including associated image information such as the soft mask.

The extracted files were stored in:

```text
/home/ubuntu/confidential/pdf_extract/
```

---

## 4.5 Inspect the Extracted Images

The extracted images were accessed through the AttackBox's file manager.

The relevant extracted image was opened using the available image viewer.

Upon inspection, the QR code could be identified in the extracted image.

This demonstrated that the QR code could be recovered from the PDF's underlying image data rather than relying solely on the rendered appearance of the original PDF.

---

## 4.6 QR Code Decoding

The recovered QR code was scanned using a QR-code scanner.

The scanner successfully decoded the QR code and revealed the secret invite code/flag required by the challenge.

**Flag:**

```text
[FLAG OBTAINED DURING THE CHALLENGE]
```

---

# 5. Findings

### Finding 1 — Embedded Images in PDF

The PDF contained multiple image objects that could be enumerated using `pdfimages`.

**Evidence:**

```bash
pdfimages -list /home/ubuntu/confidential/Repdf.pdf
```

The output identified three image-related objects, including an RGB image and its grayscale soft mask.

### Finding 2 — QR Code Recoverable From Extracted Content

Although the QR code was visually covered within the PDF, extracting the embedded image data allowed the relevant image to be inspected independently.

### Finding 3 — Secret Invite Code Successfully Recovered

The extracted QR code was successfully scanned, revealing the challenge flag.

---

# 6. Attack/Investigation Flow

```text
Repdf.pdf
    │
    ▼
Enumerate PDF images
    │
    │ pdfimages -list
    ▼
Identify embedded image objects
    │
    ▼
Create pdf_extract/
    │
    ▼
Extract images
    │
    │ pdfimages -all
    ▼
Inspect extracted images
    │
    ▼
Recover QR Code
    │
    ▼
Scan QR Code
    │
    ▼
Challenge Flag
```

---

# 7. Risk/Impact

If this technique were applicable to a real-world document containing sensitive information, simply placing an image over confidential content would **not necessarily constitute secure redaction**.

PDF documents can contain independent underlying objects. Visually covering sensitive content may leave the original information accessible through PDF object extraction or other document-forensics techniques.

### Security Recommendation

For sensitive documents, information that must be removed should be properly **redacted and sanitized**, rather than merely covered with another graphical object.

---

# 8. Conclusion

The **Confidential** challenge was successfully completed.

The investigation demonstrated that a PDF's visible content does not necessarily represent all of the underlying information stored within the document. By enumerating and extracting embedded images using `pdfimages`, the obscured QR code was recovered and subsequently decoded.

The secret invite code/flag was successfully obtained.

### Result

**Status: Successfully Completed**

**Technique:** PDF image/object extraction → QR code recovery → QR decoding

**Flag:** Obtained successfully during testing.