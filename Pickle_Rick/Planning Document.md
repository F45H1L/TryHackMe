# Planning Document — Pickle Rick

### Challenge Link: https://tryhackme.com/room/picklerick

## 1. Challenge Overview

**Challenge Name:** Pickle Rick  
**Platform:** TryHackMe  
**Target IP Address:** `<TARGET-IP>`  
**Challenge Type:** Web Application Security / Linux Privilege Escalation  
**Difficulty:** Easy  
**Primary Objective:** Identify and retrieve three hidden ingredients from the target machine to complete Rick's potion and help him transform back into a human.

### Scenario

The Pickle Rick challenge is a Rick and Morty-themed Capture the Flag (CTF) exercise. The target is a Linux server hosting a web application. The objective is to investigate the application, identify potential weaknesses, gain authorized access to the system, and locate three ingredient files.

The investigation will begin without prior knowledge of the credentials, file locations, command restrictions, or privilege configuration.

## 2. Objectives

### Primary Objectives

1. Identify the target's exposed network services.
2. Enumerate the web application and discover hidden resources.
3. Identify clues that may reveal authentication credentials.
4. Authenticate to the application's available interface.
5. Determine whether the application permits operating-system command execution.
6. Locate and retrieve the three required ingredients.
7. Investigate privilege boundaries if elevated access is necessary.
8. Document the findings and determine the security implications of any vulnerabilities discovered.

### Secondary Objectives

- Understand the relationship between web application access and Linux user privileges.
- Identify weaknesses in command filtering and privilege management.
- Practice systematic enumeration instead of relying on assumptions.
- Maintain a reproducible record of commands, observations, and results.

## 3. Scope and Rules of Engagement

### In Scope

- Target host: `<TARGET-IP>`
- Exposed services running on the target.
- HTTP resources, application authentication, and authorized command execution.
- Files and directories relevant to the three challenge objectives.
- Privilege configuration required to complete the lab.

### Out of Scope

- Attacking unrelated hosts or systems.
- Denial-of-service testing.
- Destructive modifications to the target.
- Persistence, lateral movement, or activities unrelated to the challenge objectives.

All testing must remain within the assigned TryHackMe environment.

## 4. Initial Information and Assumptions

The target IP address is provided by the challenge. No credentials, application endpoints, source-code clues, or ingredient locations are assumed to be known at the beginning.

The following hypotheses will guide the investigation:

- The target may expose a web service and other network services.
- The homepage may contain useful information in its HTML source.
- Publicly accessible resources may reveal application paths or clues.
- The application may contain an authentication mechanism.
- An authenticated interface may provide additional functionality.
- The ingredients may be stored in different locations on the filesystem.
- Linux permissions or misconfigured privilege delegation may affect access to the final ingredient.

These are hypotheses to test, not confirmed findings.

## 5. Tools and Environment

| Tool | Planned Purpose |
|---|---|
| Nmap | Discover open ports and identify running services |
| Web browser | Explore the homepage, login interface, and authenticated portal |
| cURL | Retrieve HTTP responses, headers, HTML, and public resources |
| Gobuster | Enumerate directories and files |
| Linux shell commands | Inspect files, directories, permissions, and user identity |
| `find` | Search accessible filesystem locations |
| `less`, `awk`, and other permitted utilities | Inspect file contents where appropriate |
| `sudo -l` | Assess the current user's authorized privilege delegation |

**Environment:** Kali Linux  
**Target operating system:** To be confirmed during service and application enumeration.

## 6. Planned Methodology

### Phase 1 — Network Reconnaissance

**Objective:** Determine which services are exposed by the target.

Planned command:

```bash
nmap -sC -sV -oN nmap.txt <TARGET-IP>
```

Activities:

1. Verify that the host is reachable.
2. Identify open TCP ports.
3. Determine the services and versions associated with open ports.
4. Record relevant service banners and scan results.
5. Select the most promising service for further investigation.

**Expected deliverable:** A network reconnaissance summary identifying exposed services and potential attack surfaces.

### Phase 2 — Web Application Enumeration

**Objective:** Understand the application's publicly accessible functionality.

Planned activities:

1. Open the website in a browser.
2. Inspect the homepage and its source code.
3. Identify HTML comments, referenced resources, and potentially useful clues.
4. Check publicly accessible files such as `robots.txt`.
5. Enumerate directories and files using a suitable wordlist.
6. Record discovered endpoints and their HTTP response codes.
7. Investigate authentication-related pages and redirects.

Example directory enumeration command:

```bash
gobuster dir \
  -u http://<TARGET-IP> \
  -w /usr/share/wordlists/dirb/common.txt \
  -x php,txt,html
```

**Expected deliverable:** A list of accessible pages, discovered resources, and potential entry points.

### Phase 3 — Credential Discovery and Authentication

**Objective:** Determine whether information exposed by the application can be used to authenticate legitimately within the CTF.

Activities:

1. Review source-code comments and public text resources.
2. Record any candidate usernames or password clues.
3. Identify the login form and its expected input fields.
4. Test only credentials supported by discovered evidence.
5. Observe successful or unsuccessful authentication responses.
6. Inspect the authenticated application's functionality.

**Expected deliverable:** Documented authentication findings and a description of the accessible application features.

### Phase 4 — Application Functionality and Command Execution

**Objective:** Determine whether the authenticated interface interacts with the underlying operating system.

Activities:

1. Inspect the authenticated portal.
2. Identify any command input or administrative functionality.
3. Test harmless commands to establish the execution context.
4. Record the effective user identity and current working directory.
5. Enumerate the application's directory without modifying files.
6. Identify any restrictions or filtering applied to command execution.
7. Check file permissions for discovered resources.

Example initial commands, if a command interface is provided:

```bash
whoami
pwd
ls -la
```

**Expected deliverable:** A description of the application's execution context, accessible files, and command restrictions.

### Phase 5 — Ingredient Discovery

**Objective:** Locate and read the three required ingredient files.

Activities:

1. Inspect the current application directory.
2. Review any discovered clue files.
3. Enumerate relevant home directories.
4. Search accessible filesystem locations for likely ingredient files.
5. Inspect candidate files using available, permitted utilities.
6. Record each ingredient separately and document its file location.
7. Avoid assuming that all ingredients reside in the same directory.

Example search command:

```bash
find /home /var/www -type f 2>/dev/null
```

The search scope may be expanded when justified by findings and access permissions.

**Expected deliverable:** Three documented ingredient discoveries, each linked to its corresponding file or evidence source.

### Phase 6 — Privilege Assessment

**Objective:** Determine whether the current account has access to resources unavailable to an ordinary web-server user.

Activities:

1. Identify the current effective user.
2. Review file and directory permissions.
3. Inspect authorized privilege delegation using:

```bash
sudo -l
```

4. Determine whether elevated commands are permitted.
5. If the lab configuration allows elevated access, use only the privileges necessary to retrieve the remaining challenge evidence.
6. Record the misconfiguration and explain its security impact.

Privilege escalation will be investigated only when required by the challenge objectives or supported by evidence.

**Expected deliverable:** A privilege assessment documenting the current user's permissions and any security-relevant misconfiguration.

### Phase 7 — Validation and Completion

**Objective:** Confirm that all challenge objectives have been met.

Activities:

1. Verify that all three ingredients have been retrieved.
2. Match the collected results against the room's objectives.
3. Submit the required answers through the TryHackMe interface.
4. Confirm completion in the challenge interface.
5. Preserve relevant terminal output and findings for the final report.

**Expected deliverable:** A completion record and evidence-backed summary of the investigation.

## 7. Evidence Collection Plan

The following artifacts should be preserved during the investigation:

| Evidence ID | Artifact | Purpose |
|---|---|---|
| E-01 | Nmap output | Record exposed services |
| E-02 | Homepage HTML source | Identify publicly exposed clues |
| E-03 | `robots.txt` response | Document information disclosure |
| E-04 | Gobuster results | Record discovered endpoints |
| E-05 | Authentication observations | Document the login process |
| E-06 | Command execution output | Establish the application's execution context |
| E-07 | Filesystem listings | Identify relevant files and permissions |
| E-08 | Privilege assessment output | Document privilege configuration |
| E-09 | Ingredient evidence | Verify each required objective |
| E-10 | TryHackMe completion status | Confirm challenge completion |

Sensitive values should be handled carefully when reusing these artifacts outside the lab.

## 8. Risk and Mitigation Considerations

| Potential Risk | Mitigation |
|---|---|
| Scanning the wrong host | Verify the assigned target IP before testing |
| Excessive or disruptive requests | Use conservative scan settings and avoid denial-of-service testing |
| Misinterpreting HTTP status codes | Validate endpoints through both HTTP responses and browser behavior |
| Assuming a clue is a valid credential | Confirm it through the application's normal authentication flow |
| Confusing web-server privileges with root privileges | Check the effective user and permission configuration |
| Reading inaccessible files prematurely | Inspect permissions and use only authorized access paths |
| Losing investigation evidence | Save scan results and maintain a structured activity log |

## 9. Success Criteria

The challenge will be considered complete when:

- The exposed services and web application have been enumerated.
- The application's authentication mechanism has been investigated.
- The relevant application functionality has been accessed.
- All three ingredients have been located and retrieved.
- Any privilege misconfiguration required for completion has been documented.
- The challenge objectives have been validated through the TryHackMe interface.

## 10. Final Deliverables

Upon completion of the investigation, the following documents should be prepared:

1. **Planning Document:** This document, describing the objectives, scope, tools, and proposed methodology.
2. **Instructions Document:** A reproducible sequence of steps used to solve the challenge.
3. **Technical Report:** The actual findings, evidence, commands executed, vulnerabilities identified, and security recommendations.
4. **Evidence Log:** Relevant command output, file locations, and challenge completion confirmation.

## 11. Conclusion

This plan establishes a structured approach to solving the Pickle Rick challenge from an initially unknown state. The investigation will progress through network reconnaissance, web application enumeration, authentication analysis, command execution assessment, filesystem discovery, and privilege evaluation.

Each phase will be guided by evidence gathered during the preceding phase. The specific credentials, vulnerabilities, ingredient locations, and final answers will remain unconfirmed until they are discovered and validated during the practical investigation.