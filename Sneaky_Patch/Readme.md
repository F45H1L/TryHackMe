# Sneaky Patch

### Challenge Link: https://tryhackme.com/room/hfb1sneakypatch

## Overview

**Challenge Name:** Sneaky Patch  
**Platform:** TryHackMe  
**Category:** Forensics  
**Difficulty:** Easy

### Description

A high-value system has been compromised, and suspicious activity has been detected within the Linux kernel. Traditional detection tools have failed to identify the intruder, suggesting the presence of a kernel-level backdoor.

The objective is to investigate the live Linux system, identify the suspicious kernel module, analyze its functionality, and recover the challenge flag.

## Objectives

- Investigate the compromised Linux system.
- Identify suspicious loaded kernel modules.
- Analyze the metadata and embedded strings of the suspected module.
- Discover the backdoor's interface and execution mechanism.
- Recover the challenge flag.

## Environment

- **Target OS:** Ubuntu Linux
- **Kernel Version:** `6.8.0-1016-aws`
- **Architecture:** x86-64
- **Access Method:** SSH
- **Initial User:** `ubuntu`
- **Privilege Level:** Root access available through `sudo`

## Tools Used

- `ssh` — Remote system access
- `uname` — Kernel and system information
- `lsmod` — List loaded kernel modules
- `modinfo` — Inspect kernel module metadata
- `strings` — Extract readable strings from binary files
- `grep` — Search for relevant strings and module references
- `xxd` — Decode hexadecimal data

## Investigation Steps

### 1. Connect to the Target

Connect to the TryHackMe machine using the SSH credentials provided by the room.

```bash
ssh ubuntu@<TARGET_IP>
```

Replace `<TARGET_IP>` with the target machine's IP address.

### 2. Enumerate the System

Identify the current user, privileges, hostname, and kernel version.

```bash
whoami
id
uname -a
```

The system was running Ubuntu with kernel version `6.8.0-1016-aws`.

### 3. Inspect Loaded Kernel Modules

List the currently loaded kernel modules.

```bash
lsmod
```

The output contained an unfamiliar module named `spatch`.

This module was selected for further investigation because its name stood out in the context of a kernel-backdoor challenge.

### 4. Check Privileges

Determine which commands the current user can execute through `sudo`.

```bash
sudo -l
```

The output confirmed that the `ubuntu` user had unrestricted sudo privileges, including passwordless execution.

### 5. Analyze the Suspicious Module

Inspect the module metadata.

```bash
sudo modinfo spatch
```

Relevant findings:

- **Module:** `spatch`
- **Description:** `Cipher is always root`
- **Author:** `Cipher`
- **License:** `GPL`
- **Location:** `/lib/modules/6.8.0-1016-aws/kernel/drivers/misc/spatch.ko`

The description and author fields were suspicious in the context of the investigation and warranted further analysis.

### 6. Extract Embedded Strings

Use the `strings` utility to inspect readable text embedded in the module.

```bash
strings /lib/modules/$(uname -r)/kernel/drivers/misc/spatch.ko
```

The output revealed several important strings:

```text
get_flag
cipher_bd
/tmp/cipher_output.txt
/bin/sh
/root/src/spatch.c
HOME=/root
[CIPHER BACKDOOR] Module loaded. Write data to /proc/%s
[CIPHER BACKDOOR] Format: echo "COMMAND" > /proc/cipher_bd
[CIPHER BACKDOOR] Executing command: %s
[CIPHER BACKDOOR] Command Output: %s
[CIPHER BACKDOOR] Here's the secret: 54484d7b73757033725f736e33346b795f643030727d0a
```

These strings indicated that the module exposed a custom `/proc` interface, executed shell commands, and captured command output in a temporary file.

The embedded `get_flag` and secret-related strings also provided a direct lead toward recovering the flag.

### 7. Identify the Backdoor Interface

The module revealed the following interface:

```text
/proc/cipher_bd
```

It also referenced the output file:

```text
/tmp/cipher_output.txt
```

The embedded messages suggested that commands written to the `/proc` interface were executed by the module and that their output was captured.

This behavior is consistent with a privileged command-execution backdoor.

### 8. Decode the Embedded Secret

The module contained the following hexadecimal value:

```text
54484d7b73757033725f736e33346b795f643030727d0a
```

Decode it using `xxd`:

```bash
echo '54484d7b73757033725f736e33346b795f643030727d0a' | xxd -r -p
```

The decoded output revealed the TryHackMe flag.

## Flag

```text
THM{sup3r_sn34ky_d00r}
```

## Key Findings

| Artifact | Finding |
|---|---|
| Suspicious kernel module | `spatch.ko` |
| Module author | `Cipher` |
| Module description | `Cipher is always root` |
| Backdoor interface | `/proc/cipher_bd` |
| Command output file | `/tmp/cipher_output.txt` |
| Embedded source path | `/root/src/spatch.c` |
| Secret format | Hexadecimal |
| Flag recovery tool | `xxd -r -p` |