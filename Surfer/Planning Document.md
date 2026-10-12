# Planning Document — Surfer

### Challenge Link: https://tryhackme.com/room/surfer

## 1. Challenge Overview

- **Challenge Name:** Surfer
- **Platform:** TryHackMe
- **Target IP:** `<TARGET-IP>`
- **Target URL:** `http://<TARGET-IP>`
- **Target Type:** Web application
- **Assessment Type:** Authorized Capture the Flag (CTF) security assessment
- **Primary Objective:** Identify and exploit the vulnerability or vulnerabilities that expose the challenge flag.
- **Assessment Status:** Planned — investigation not yet started

## 2. Objectives

The primary objectives of this assessment are to:

1. Discover the web application's accessible pages, directories, and endpoints.
2. Identify authentication mechanisms and assess their security.
3. Examine exposed files and application functionality for useful clues.
4. Investigate how the application handles user-controlled input.
5. Identify potential access-control weaknesses and server-side request vulnerabilities.
6. Retrieve the challenge flag through a controlled proof of concept.
7. Document the findings, exploitation methodology, and recommended remediation.

## 3. Scope

### In Scope

- The challenge web application hosted at `<TARGET-IP>`.
- Publicly accessible pages, directories, and files.
- Authentication and session-handling mechanisms.
- Application endpoints identified during reconnaissance.
- URL-processing and document-generation functionality, if present.
- Internal resources accessible through the application's own functionality, where permitted by the challenge.

### Out of Scope

- Systems unrelated to the challenge.
- Denial-of-service attacks or destructive testing.
- Persistence, lateral movement, and unnecessary data extraction.
- Testing against external systems outside the authorized environment.

## 4. Initial Hypotheses

The following are hypotheses to investigate, not confirmed findings.

| ID | Hypothesis | Planned verification |
|---|---|---|
| H1 | The application may expose sensitive information through files or directories. | Inspect `robots.txt`, enumerate directories, and review accessible resources. |
| H2 | Authentication may use weak or default credentials. | Inspect the login flow and evaluate credentials only within the authorized challenge. |
| H3 | Internal application pages may enforce access restrictions. | Identify internal endpoints and compare direct-access behavior with application-mediated access. |
| H4 | A document-generation feature may process user-controlled URLs. | Inspect forms and intercept requests involving report or PDF generation. |
| H5 | Server-side URL fetching may permit access to internal resources. | If URL-fetching functionality is found, test it with controlled requests to permitted local endpoints. |

## 5. Planned Methodology

### Phase 1: Environment Preparation

**Objective:** Confirm that the target is reachable and prepare the assessment tools.

Planned tools:

- Kali Linux
- Firefox
- Burp Suite Community Edition
- `curl`
- Gobuster
- `nmap`
- `pdftotext` or another PDF inspection utility, if required

Initial connectivity check:

```bash
ping -c 4 <TARGET-IP>
```

Check the web server response:

```bash
curl -i http://<TARGET-IP>/
```

A failed ping does not necessarily mean the target is unavailable because ICMP traffic may be blocked.

### Phase 2: Service and Web Reconnaissance

**Objective:** Identify exposed services and understand the web application's structure.

Perform a targeted service scan:

```bash
nmap -sV -sC -p 80 <TARGET-IP>
```

Inspect common discovery files:

```bash
curl -i http://<TARGET-IP>/robots.txt
```

Enumerate directories and files:

```bash
gobuster dir \
  -u http://<TARGET-IP>/ \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,bak
```

Record discovered paths, HTTP status codes, redirects, and any potentially sensitive files.

### Phase 3: Application Mapping

**Objective:** Understand the application's available functionality and request flow.

Planned activities:

1. Open the application in Firefox.
2. Inspect the login page and identify the submitted form fields.
3. Review authentication responses and redirects.
4. Examine pages available after authentication, if access is obtained.
5. Identify forms that generate reports, export data, or process URLs.
6. Record relevant endpoints, HTTP methods, parameters, and session requirements.

Burp Suite will be used to intercept and inspect HTTP requests and responses.

### Phase 4: Authentication and Information Disclosure Testing

**Objective:** Determine whether the application exposes credentials, internal paths, or other useful information.

Planned checks:

- Inspect accessible backup files and application metadata.
- Review comments, links, and navigation elements for additional endpoints.
- Check for weak authentication only within the authorized challenge scope.
- Examine session cookies and determine which requests require authentication.
- Compare access to potentially restricted pages before and after authentication.

Any discovered credentials will be documented as evidence and tested only against the challenge application.

### Phase 5: Input and URL-Handling Assessment

**Objective:** Investigate whether application features trust user-controlled input.

If a report-generation or PDF-export feature exists:

1. Intercept the relevant HTTP request using Burp Suite.
2. Identify the input parameters accepted by the endpoint.
3. Determine whether any parameter accepts a URL.
4. Observe how the application processes a normal, permitted URL.
5. Test controlled variations to assess URL validation and server-side fetching.
6. Review the resulting HTTP response and any generated document for evidence of unintended internal-resource access.

Testing should remain limited to the authorized target and controlled local resources.

### Phase 6: Access-Control and Internal Resource Testing

**Objective:** Assess whether internal pages can be accessed through application functionality despite direct-access restrictions.

Planned activities:

- Identify internal paths from application links, exposed files, or server responses.
- Request identified paths directly and record the response.
- If a server-side URL-fetching feature is discovered, assess whether it can access the same resources.
- Compare direct access with application-mediated access.
- Determine whether sensitive content is returned in a response or embedded in a generated file.

### Phase 7: Proof of Concept and Flag Retrieval

**Objective:** Demonstrate the vulnerability and retrieve the challenge flag.

After identifying a plausible vulnerability:

1. Prepare a minimal, reproducible proof of concept.
2. Submit a controlled request using the vulnerable application functionality.