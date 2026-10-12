# Penetration Testing Report — Surfer

## 1. Executive Summary

This report documents the security assessment performed against the TryHackMe Surfer web application. The objective was to identify security weaknesses, investigate the application's exposed functionality, and retrieve the challenge flag through a reproducible proof of concept.

The assessment began with web reconnaissance and directory enumeration. An exposed backup conversation provided clues about the application's PDF export feature and an internal page. After authenticating to the application, the PDF export request was intercepted and examined using Burp Suite.

Testing demonstrated that the PDF-generation functionality accepted a user-controlled URL and could retrieve an internal application resource. By changing the URL parameter to reference a local internal page, the application generated a PDF containing the challenge flag.

The principal finding was a **Server-Side Request Forgery (SSRF)** vulnerability in the PDF export workflow.

### Assessment Summary

| Attribute | Details |
|---|---|
| Target | TryHackMe Surfer |
| Target IP | `<TARGET-IP>` |
| Target URL | `http://<TARGET-IP>` |
| Assessment Type | Authorized CTF web application assessment |
| Primary Finding | Server-Side Request Forgery (SSRF) |
| Authentication | Successful using challenge credentials |
| Result | Challenge flag retrieved |
| Status | Completed |

## 2. Objectives

The assessment aimed to:

- Identify exposed web application resources and endpoints.
- Examine the application's authentication and session behavior.
- Investigate information disclosure through publicly accessible files.
- Analyze the PDF export feature and its URL-processing behavior.
- Test whether internal resources could be retrieved through server-side requests.
- Retrieve the challenge flag and document the exploitation process.
- Recommend security controls to prevent similar vulnerabilities.

## 3. Scope and Limitations

### 3.1 In Scope

The assessment was limited to the assigned challenge environment:

- Web application hosted at `<TARGET-IP>`.
- Publicly accessible files and directories.
- Application authentication and session handling.
- The PDF export endpoint.
- Internal application resources involved in the challenge.

### 3.2 Limitations

The assessment focused on the challenge's web application and the path required to retrieve the flag. It was not a comprehensive infrastructure audit, source-code review, or production penetration test.

No conclusions are made about vulnerabilities that were not tested or supported by observed evidence.

## 4. Methodology

The assessment followed a structured web application testing process:

1. Initial connectivity and service discovery.
2. Web reconnaissance and directory enumeration.
3. Information disclosure analysis.
4. Authentication and application functionality testing.
5. HTTP request interception and parameter analysis.
6. Controlled testing of server-side URL processing.
7. Flag extraction and evidence verification.
8. Remediation planning.

## 5. Tools and Technologies

| Tool | Purpose |
|---|---|
| Kali Linux | Testing environment |
| Nmap | Service discovery and version detection |
| cURL | HTTP requests and response inspection |
| Gobuster | Directory and file enumeration |
| Firefox | Web application interaction |
| Burp Suite Community Edition | HTTP request interception and modification |
| `pdftotext` | Text extraction from generated PDF files |

## 6. Technical Findings

### Finding F-01: Server-Side Request Forgery in PDF Export

**Severity:** High potential impact; context-dependent

**Vulnerability Class:** Server-Side Request Forgery (SSRF)

**Affected Endpoint:** `/export2pdf.php`

**Affected Parameter:** `url`

**CWE Reference:** CWE-918 — Server-Side Request Forgery (SSRF)

#### 6.1 Description

The PDF export functionality accepted a URL through an HTTP POST parameter and used it to generate a PDF report.

The original form supplied the following URL:

```text
http://127.0.0.1/server-info.php
```

The presence of a user-controlled URL in a server-side document-generation workflow introduced the possibility that the application could be induced to fetch unintended resources.

During testing, a separate internal endpoint, `/internal/admin.php`, was identified. Direct access to that endpoint returned the following message:

```text
This page can only be accessed locally.
```

This response indicated that the page applied a local-access restriction.

The PDF export functionality was then tested to determine whether the server itself could retrieve the internal resource.

#### 6.2 Evidence of Information Disclosure

The application exposed a backup conversation at:

```text
/backup/chat.txt
```

The file contained references to the PDF export tool and an internal server expected to serve the challenge flag. These clues helped direct the subsequent investigation.

Directory enumeration also identified the internal admin page:

```text
/internal/admin.php
```

Together, these observations supported investigating whether the PDF export functionality could access resources unavailable through direct requests.

#### 6.3 Proof of Concept

The following request body was observed during the normal PDF export operation:

```http
POST /export2pdf.php HTTP/1.1
Host: <TARGET-IP>
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=<authenticated-session-cookie>

url=http%3A%2F%2F127.0.0.1%2Fserver-info.php
```

The URL parameter was modified to reference the internal admin page.

**Modified parameter:**

```text
url=http%3A%2F%2F127.0.0.1%2Finternal%2Fadmin.php
```

Equivalent decoded value:

```text
http://127.0.0.1/internal/admin.php
```

The modified request was submitted through Burp Suite Repeater using the authenticated session.

#### 6.4 Observed Result

The application generated a PDF containing the following text:

```text
Report generated for http://127.0.0.1/internal/admin.php
flag{6255c55660e292cf0116c053c9937810}
```

This result confirmed that the PDF-generation workflow retrieved content associated with the internal page and exposed it through the generated document.

#### 6.5 Impact

An attacker able to access the vulnerable functionality could potentially use it to make the server request resources that are not directly accessible from the attacker's browser.

Depending on the application's network permissions and URL validation controls, potential consequences include:

- Disclosure of internal application pages.
- Access to sensitive resources exposed only to local requests.
- Retrieval of internal service responses.
- Exposure of confidential data through generated reports.
- Further exploitation of reachable internal services, depending on their functionality and authentication requirements.

The demonstrated impact in this assessment was retrieval of the challenge flag from an internal page.

#### 6.6 Root Cause

The observed behavior was consistent with insufficient validation of the user-supplied URL in the PDF-generation workflow.

The server-side component was able to fetch a loopback URL, and the resulting document exposed the internal page's content. This created a trust boundary issue between user-controlled input and server-side network access.

The assessment established the behavior through a proof of concept; the precise implementation-level cause would require source-code review to confirm.

#### 6.7 Remediation

Recommended mitigations include:

1. **Strict destination allowlisting:** Permit only explicitly approved URLs or hosts required by the application.
2. **IP address validation:** Reject loopback, private, link-local, and other prohibited IP ranges after resolving hostnames.
3. **Redirect validation:** Revalidate destinations after each HTTP redirect to prevent validation bypasses.
4. **Network isolation:** Run the PDF-generation component in a restricted environment without unnecessary access to internal services.
5. **Avoid arbitrary URL fetching:** Generate reports from trusted application data wherever possible.
6. **Independent authorization:** Ensure internal endpoints authenticate and authorize requests independently instead of relying solely on localhost restrictions.
7. **Monitoring and logging:** Record rejected URL destinations and unusual internal-resource access attempts.
8. **Regression testing:** Add tests verifying that the PDF export function cannot access prohibited internal destinations.

## 7. Supporting Observations

### 7.1 Information Disclosure Through Backup Files

The `robots.txt` file disclosed the path `/backup/chat.txt`.

The backup conversation revealed details about application functionality and internal resources.

**Security implication:** Sensitive files should not be placed in publicly accessible directories. `robots.txt` is a crawler directive, not an access-control mechanism.

**Recommendation:** Remove sensitive backup files from the web root, restrict access to operational artifacts, and prevent deployment of internal communications to public directories.

### 7.2 Weak Authentication Credentials

The credentials below successfully authenticated during the challenge:

```text
Username: admin
Password: admin
```

**Security implication:** Easily guessable credentials can allow unauthorized users to reach functionality that should be restricted.

**Recommendation:** Enforce strong, unique credentials; remove default accounts and passwords; apply appropriate login protections; and use multifactor authentication where suitable.

The credential finding was observed in the challenge environment. The assessment did not establish whether the same credentials were reused elsewhere.

### 7.3 Internal Resource Access Restrictions

Direct access to `/internal/admin.php` returned a local-access restriction message, while the PDF export workflow was able to retrieve its content.

**Security implication:** Local-only restrictions are insufficient if another application feature can proxy requests to the protected resource.

**Recommendation:** Enforce authentication and authorization at the internal endpoint itself, and constrain server-side components that make outbound requests.

## 8. Risk Assessment

The SSRF finding has the potential for significant impact because server-side requests may reach resources unavailable to external clients. However, the severity of a real-world deployment depends on the privileges of the vulnerable component, network reachability, sensitivity of accessible resources, and the effectiveness of existing controls.

| Risk factor | Assessment |
|---|---|
| Attack vector | Web application request |
| Authentication requirement | Authenticated session was used in this test |
| Demonstrated impact | Internal content disclosure |
| Potential confidentiality impact | High, depending on reachable resources |
| Integrity impact | Not demonstrated |
| Availability impact | Not demonstrated |
| Overall priority | High priority for remediation; formal CVSS scoring not performed |

The severity classification is a qualitative assessment based on the demonstrated behavior and potential consequences. It is not a formally calculated CVSS score.

## 9. Challenge Flag

The following flag was extracted from the generated PDF:

```text
flag{6255c55660e292cf0116c053c9937810}
```

This confirms successful completion of the flag-retrieval objective.

## 10. Lessons Learned

The challenge demonstrated several important web application security principles:

- Files exposed through web directories can reveal sensitive implementation details.
- Directory enumeration helps identify application endpoints that are not linked from the main interface.
- Burp Suite allows security testers to inspect and modify HTTP parameters to validate application behavior.
- User-controlled URLs in server-side processing features can introduce SSRF vulnerabilities.
- Localhost restrictions do not replace proper authorization.
- PDF generation and other server-side integrations should be treated as security-sensitive components.
- Effective remediation requires both application-layer validation and network-level restrictions.

## 11. Conclusion

The Surfer challenge was completed successfully by identifying and exploiting an SSRF vulnerability in the application's PDF export workflow.

Reconnaissance uncovered a backup conversation that provided clues about the export tool and internal resources. Subsequent enumeration identified an internal admin page that rejected direct external access. By intercepting the PDF export request and changing its URL parameter to the local internal page, the server generated a PDF containing the challenge flag.

The primary remediation priorities are to strictly validate URL destinations, isolate server-side document-generation components, and enforce authentication and authorization independently on internal endpoints. The exposed backup file and weak challenge credentials should also be addressed as separate security concerns.

## 12. References

- OWASP — [Server-Side Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- PortSwigger Web Security Academy — [Server-Side Request Forgery (SSRF)](https://portswigger.net/web-security/ssrf)
- MITRE CWE — [CWE-918: Server-Side Request Forgery (SSRF)](https://cwe.mitre.org/data/definitions/918.html)
- TryHackMe — [Official Platform](https://tryhackme.com/)