# Security Investigation Report — Sneaky Patch

## 1. Executive Summary

**Platform:** TryHackMe  
**Challenge:** Sneaky Patch  
**Category:** Forensics  
**Difficulty:** Easy  
**Target Host:** `tryhackme`  
**Operating System:** Ubuntu Linux  
**Kernel Version:** `6.8.0-1016-aws`  
**Investigation Type:** Live system and kernel module investigation  
**Status:** Challenge flag recovered

The investigation focused on a compromised Linux system suspected of running a kernel-level backdoor. Initial enumeration revealed a suspicious loaded kernel module named `spatch`. Analysis of the module's metadata and embedded strings identified indicators of privileged command execution through a custom `/proc` interface.

A hexadecimal secret embedded in the module was decoded, successfully recovering the TryHackMe challenge flag.

The findings indicate that the module was designed to provide a concealed or nonstandard privileged command-execution mechanism. The investigation demonstrates how kernel module analysis can reveal malicious functionality that may not be apparent through routine user-space inspection.

## 2. Objectives

The investigation aimed to:

1. Enumerate the compromised Linux system and determine the current privilege level.
2. Identify suspicious loaded kernel modules.
3. Examine the metadata of the suspected module.
4. Extract and analyze embedded strings from the module binary.
5. Identify the backdoor's communication interface and command-execution behavior.
6. Recover the embedded challenge flag.
7. Document the findings and recommend appropriate defensive measures.

## 3. Environment and Scope

### 3.1 Target Information

| Attribute | Observed Value |
|---|---|
| Hostname | `tryhackme` |
| Initial User | `ubuntu` |
| User ID | `1000` |
| Operating System | Ubuntu Linux |
| Kernel Version | `6.8.0-1016-aws` |
| Architecture | x86-64 |
| Initial Access | SSH |
| Privilege Escalation | Passwordless sudo available |
| Suspicious Module | `spatch` |

### 3.2 Scope

The investigation covered the live target system, its loaded kernel modules, the metadata of the suspicious module, and strings embedded in the module binary.

The objective was to analyze the provided challenge environment and recover its flag. This report does not claim that a complete forensic image, memory acquisition, or independent kernel integrity verification was performed.

## 4. Methodology

The investigation followed a structured process:

1. **System enumeration:** Identify the host, operating system, kernel version, and user privileges.
2. **Module enumeration:** Review loaded kernel modules and identify unusual entries.
3. **Metadata analysis:** Inspect the suspected module using `modinfo`.
4. **Binary string analysis:** Extract embedded strings using `strings`.
5. **Indicator analysis:** Identify the custom `/proc` interface, command-execution references, and embedded hexadecimal secret.
6. **Flag recovery:** Decode the hexadecimal data using `xxd`.
7. **Documentation:** Record the evidence and derive defensive recommendations.

## 5. Technical Investigation

### 5.1 Initial System Enumeration

The following commands were executed:

```bash
whoami
id
uname -a
```

The `whoami` command returned:

```text
ubuntu
```

The `id` command confirmed that the account had UID `1000` and belonged to the `sudo` group, among others.

The kernel identification command returned:

```text
Linux tryhackme 6.8.0-1016-aws #17-Ubuntu SMP
Mon Sep 2 13:48:07 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux
```

**Analysis:** The target was a 64-bit Ubuntu Linux system running an AWS-oriented kernel. The account's group membership suggested that elevated access might be possible, which was subsequently confirmed through sudo policy inspection.

### 5.2 Loaded Kernel Module Enumeration

The following command was executed:

```bash
lsmod
```

An unfamiliar module appeared near the top of the output:

```text
Module    Size    Used by
spatch    12288   0
```

**Observation:** The `spatch` module was loaded into the running kernel.

**Analysis:** The module name was considered suspicious in the context of the challenge. Its presence alone did not prove malicious activity, but it justified further inspection.

### 5.3 Privilege Assessment

The following command was executed:

```bash
sudo -l
```

The output included:

```text
User ubuntu may run the following commands on tryhackme:
    (ALL : ALL) ALL
    (ALL) NOPASSWD: ALL
```

**Observation:** The account could execute commands with elevated privileges through `sudo` without a password.

**Analysis:** Root-level inspection was available without exploiting an additional privilege-escalation vulnerability. This enabled further examination of the kernel module and its metadata.

### 5.4 Kernel Module Metadata Analysis

The following command was executed:

```bash
sudo modinfo spatch
```

Relevant output:

```text
filename:       /lib/modules/6.8.0-1016-aws/kernel/drivers/misc/spatch.ko
description:    Cipher is always root
author:         Cipher
license:        GPL
srcversion:     81BE8A2753A1D8A9F28E91E
depends:
name:           spatch
vermagic:       6.8.0-1016-aws SMP mod_unload modversions
```

**Key observations:**

- The module was located at `/lib/modules/6.8.0-1016-aws/kernel/drivers/misc/spatch.ko`.
- Its description was `Cipher is always root`.
- The declared author was `Cipher`.
- The module's version magic matched the running kernel version.

**Analysis:** The description and author fields were notable indicators in the context of the challenge. The matching kernel version was consistent with the module being built for the running kernel, but did not establish its legitimacy or integrity.

Metadata fields can be deliberately chosen by a module author and should not be treated as independently verified attribution.

### 5.5 Embedded String Extraction

The following command was used to inspect the binary:

```bash
strings /lib/modules/$(uname -r)/kernel/drivers/misc/spatch.ko
```

The output included the following strings:

```text
get_flag
cipher_bd
/tmp/cipher_output.txt
/bin/sh
%s > %s 2>&1
get_flag
/root/src/spatch.c
HOME=/root
[CIPHER BACKDOOR] Failed to create /proc entry
[CIPHER BACKDOOR] Module loaded. Write data to /proc/%s
[CIPHER BACKDOOR] Module unloaded.
[CIPHER BACKDOOR] Failed to read output file
[CIPHER BACKDOOR] Command Output: %s
[CIPHER BACKDOOR] No output captured.
[CIPHER BACKDOOR] Executing command: %s
[CIPHER BACKDOOR] Failed to setup usermode helper.
[CIPHER BACKDOOR] Format: echo "COMMAND" > /proc/cipher_bd
[CIPHER BACKDOOR] Try: echo "%s" > /proc/cipher_bd
[CIPHER BACKDOOR] Here's the secret: 54484d7b73757033725f736e33346b795f643030727d0a
```

**Analysis:**

The extracted strings provided the strongest evidence in the investigation.

| String | Significance |
|---|---|
| `cipher_bd` | Identifies the custom backdoor interface |
| `/proc/cipher_bd` | Reveals the expected `/proc` path |
| `/bin/sh` | Indicates shell execution functionality |
| `/tmp/cipher_output.txt` | Identifies the referenced command-output file |
| `get_flag` | Suggests flag-related functionality |
| `/root/src/spatch.c` | Reveals a source-file path embedded in the binary |
| `Here's the secret:` | Introduces the embedded hexadecimal value |
| `Executing command: %s` | Indicates command-execution logging |
| `Command Output: %s` | Indicates output reporting functionality |

The strings strongly suggest that the module was designed to accept commands through a custom `/proc` interface, invoke a shell, and capture command output.

The binary also contained a hexadecimal secret that could be decoded independently of the module's runtime interface.

### 5.6 Identification of the Backdoor Mechanism

The module explicitly referenced the following command format:

```text
echo "COMMAND" > /proc/cipher_bd
```

The associated strings indicated that the module expected input through `/proc/cipher_bd`.

The module also referenced `/tmp/cipher_output.txt` and included messages concerning command execution and captured output.

**Analysis:** These indicators are consistent with a privileged command-execution backdoor implemented through a custom kernel interface. The interface provides a route for submitting commands, while the embedded strings suggest that command output is redirected to a temporary file and reported back.

The runtime behavior was inferred from the binary's embedded strings; a separate controlled command-execution test was not required for flag recovery.

### 5.7 Hexadecimal Secret Recovery

The embedded secret was:

```text
54484d7b73757033725f736e33346b795f643030727d0a
```

The value was decoded using:

```bash
echo '54484d7b73757033725f736e33346b795f643030727d0a' | xxd -r -p
```

The command returned:

```text
THM{sup3r_sn34ky_d00r}
```

**Analysis:** The hexadecimal data decoded into a valid TryHackMe-style flag. The final byte, `0a`, represents a newline character.

This recovered the challenge flag without requiring additional interaction with the suspected backdoor interface.

## 6. Findings Summary

| Finding | Evidence | Assessment |
|---|---|---|
| Suspicious kernel module | `spatch` present in `lsmod` | Requires investigation |
| Suspicious module metadata | `Cipher` author and `Cipher is always root` description | Strong contextual indicator |
| Custom kernel interface | `/proc/cipher_bd` | Backdoor interface indicated |
| Shell execution functionality | `/bin/sh` and command-execution strings | Privileged execution mechanism indicated |
| Command-output capture | `/tmp/cipher_output.txt` | Output capture mechanism indicated |
| Embedded challenge secret | Hexadecimal string in the module | Confirmed |
| Challenge flag | Successful hexadecimal decoding | Recovered |

## 7. Impact Assessment

If deployed on a real system with the behavior indicated by the embedded strings, this type of module could present a serious security risk.

Potential impacts include:

- **Privilege abuse:** A command-execution interface associated with elevated privileges could allow unauthorized administrative operations.
- **Stealth and evasion:** Kernel-level components may interfere with ordinary system inspection, depending on their implementation.
- **Persistence:** A malicious module may be configured to load automatically or survive normal user-space process termination. Automatic persistence was not independently verified in this investigation.
- **Confidentiality and integrity risks:** Privileged command execution could enable unauthorized access to files, credentials, system configuration, and other sensitive resources.

The precise extent of concealment, persistence, and system compromise was not independently established through a full forensic examination.

## 8. Remediation Recommendations

For a real-world incident involving a suspected malicious kernel module, the following actions are recommended.

### 8.1 Preserve Evidence

- Record the system state and collect relevant logs.
- Preserve the module binary and calculate a cryptographic hash.
- Acquire volatile evidence using approved forensic procedures.
- Document all investigative commands and timestamps.

### 8.2 Isolate the Compromised Host

- Restrict network connectivity using the incident-response process.
- Avoid unnecessary changes to the running system before volatile evidence is collected.
- Prevent further unauthorized access while preserving evidence.

### 8.3 Investigate Persistence

- Review module-loading configuration under `/etc/modules`, `/etc/modules-load.d/`, and related locations.
- Inspect relevant systemd units and startup scripts.
- Examine kernel logs and authentication records for suspicious activity.
- Verify the integrity and provenance of installed kernel modules.

### 8.4 Eradicate and Recover

- Do not rely solely on deleting the suspicious module file.
- Rebuild the system from a trusted image if kernel compromise is confirmed.
- Restore data from verified backups.
- Rotate credentials and secrets that may have been exposed.
- Apply security updates and review module-loading restrictions.

### 8.5 Improve Detection

- Monitor unexpected kernel module loads and changes to module directories.
- Restrict privileged access according to least-privilege principles.
- Consider Secure Boot, kernel lockdown, and module-signature enforcement where supported.
- Use trusted baselines and endpoint monitoring to detect deviations from expected system behavior.

## 9. Limitations

This investigation recovered the challenge flag by analyzing the suspicious module's embedded strings. The following activities were not documented as completed:

- Full memory acquisition and analysis.
- Complete forensic disk imaging.
- Independent source-code review of `/root/src/spatch.c`.
- Cryptographic comparison against a trusted module baseline.
- Controlled testing of every backdoor command.
- Verification of automatic persistence across reboot.
- Assessment of other potential compromise indicators on the host.

Accordingly, the report distinguishes observed evidence from conclusions inferred from the binary's strings.

## 10. Conclusion

The Sneaky Patch investigation identified a suspicious Linux kernel module named `spatch`. Its metadata contained challenge-related clues, while its embedded strings revealed a custom `/proc` interface, shell-execution references, command-output capture, and a hexadecimal secret.

Decoding the secret with `xxd -r -p` successfully recovered the flag:

```text
THM{sup3r_sn34ky_d00r}
```

The challenge demonstrates the value of combining system enumeration, kernel module metadata inspection, binary string analysis, and hexadecimal decoding during Linux forensic investigations.

**Final Status:** Challenge flag recovered successfully.

## 11. References

- TryHackMe — Sneaky Patch challenge.
- Linux manual pages: `lsmod(8)`, `modinfo(8)`, `strings(1)`, and `xxd(1)`.
- Linux kernel documentation on loadable modules and kernel security mechanisms.