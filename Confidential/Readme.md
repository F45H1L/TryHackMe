Room Access Link: https://tryhackme.com/room/confidential?vccr=1
1. Since the PDF is local to the AttackBox, let's first navigate the directory where the file is located:
```bash
cd /home/ubuntu/confidential
```
2. List the files from the current directory:
```bash
ls -la
```
We have a PDF file Repdf.pdf.

3. Listing Images from the PDF file:
```bash
pdfimages -list /home/ubuntu/confidential/Repdf.pdf
```
page   num  type   width height color comp bpc  enc interp  object ID x-ppi y-ppi size ratio
--------------------------------------------------------------------------------------------
   1     0 image     850  1100  gray    1   8  image  yes       10  0    73    73 85.7K 9.4%
   1     1 image     187   169  rgb     3   8  image  yes       13  0    73    73 9060B 9.6%
   1     2 smask     187   169  gray    1   8  image  yes       13  0    73    73 3150B  10%

4. Create a directory to save the images from the PDF
```bash
mkdir pdf_extract
```

5. Extract the images from the PDF into the directory /pdf_extract:
```bash
pdfimages -all /home/ubuntu/confidential/Repdf.pdf pdf_extract/image
```

6. Open the folder on the local system of the TryHackMe's attackbox and open the image of the PDF on an image viewer.

7. Scan the QR Code with your phone obtain the Flag!