# Testing Report

## TryHackMe – Committed

**Platform:** TryHackMe
**Challenge:** Committed
**Testing Type:** Authorized CTF/Lab Assessment
**Target:** `/home/ubuntu/commited`
**Assessment Focus:** Git Repository / Source Code / Commit History Analysis

---

## 1. Executive Summary

The objective of this assessment was to investigate a Git repository for sensitive information that had allegedly been accidentally committed by a developer.

The assessment began by locating and extracting the provided ZIP archive, followed by verification and enumeration of the Git repository. Branches, commit history, repository statistics, current files, and source code were reviewed.

During the Git history analysis, a suspicious commit named **`Oops`** was identified:

```text
c56c470 Oops
```

The commit was subsequently inspected using:

```bash
git show c56c470
```

This commit was identified as the primary point of interest for the investigation because of its suspicious commit message and its position within the repository history.

---

# 2. Scope

The assessment was limited to the TryHackMe-provided environment.

### Target Directory

```text
/home/ubuntu/commited
```

### In-Scope Activities

* ZIP archive inspection
* Extraction of the provided repository
* Git repository verification
* Branch enumeration
* Commit history analysis
* Repository statistics analysis
* Current file inspection
* Source-code inspection
* Investigation of suspicious commits

### Out of Scope

* External systems
* Real-world GitHub repositories
* Unauthorized access
* Destructive activity
* Credential attacks against external services

---

# 3. Testing Methodology

The following methodology was used:

1. Locate the challenge files.
2. Inspect the supplied ZIP archive.
3. Extract the repository.
4. Enter the extracted Git repository.
5. Verify the repository state.
6. Enumerate branches and commits.
7. Analyze commit history.
8. Inspect current repository files.
9. Identify suspicious commits.
10. Examine the suspicious commit in detail.

---

# 4. Detailed Testing Procedure

## 4.1 Navigate to the Working Directory

The first step was to navigate to the directory containing the challenge files.

```bash
cd /home/ubuntu/commited
```

This established the working directory for the investigation.

---

## 4.2 List Directory Contents

The directory contents were enumerated using:

```bash
ls -la
```

The purpose of this step was to identify the files supplied with the challenge and determine whether an archive or repository was present.

---

## 4.3 Inspect the ZIP Archive

The contents of the supplied archive were inspected without extracting it:

```bash
unzip -l commited.zip
```

This allowed the structure of the archive to be reviewed before extraction.

---

## 4.4 Extract the Repository

The archive was extracted using:

```bash
unzip commited.zip
```

The extracted files included the Git repository required for further analysis.

---

## 4.5 Enter the Repository

The extracted repository directory was accessed:

```bash
cd commited
```

---

## 4.6 Verify Git Repository Status

The repository status was checked using:

```bash
git status
```

This confirmed that the extracted directory was a Git repository and provided information about the current branch and working-tree state.

---

# 5. Git Repository Enumeration

## 5.1 Branch Enumeration

All available branches were examined using:

```bash
git branch -a
```

The purpose was to determine whether multiple branches existed and whether potentially sensitive information could exist outside the currently checked-out branch.

---

## 5.2 Git History Analysis

The repository history was examined using:

```bash
git log --all --oneline --decorate --graph
```

This provided a compact graphical representation of the repository's commit history.

The `--all` option was used to ensure that commits associated with available references were included in the investigation.

---

## 5.3 Commit Statistics

The commit history was further examined with:

```bash
git log --all --stat
```

This provided information about files changed by individual commits and helped identify commits that warranted further investigation.

---

# 6. Current Repository Analysis

The current directory contents were enumerated:

```bash
ls -la
```

The purpose was to identify the files currently present in the working tree.

The identified files were then inspected individually.

---

## 6.1 Readme Analysis

The repository README was inspected:

```bash
cat Readme.md
```

The README was reviewed for information that could provide context about the application, repository, or challenge.

---

## 6.2 Source Code Analysis

The main Python source file was inspected:

```bash
cat main.py
```

The source code was reviewed to understand the application's current implementation and identify potentially interesting functionality or references to sensitive information.

---

# 7. Suspicious Commit Identification

During the Git history analysis, the following commit was identified as suspicious:

```text
Commit: c56c470
Message: Oops
```

The commit message **`Oops`** suggested that the commit may have represented an accidental change or an attempted correction.

Because the challenge specifically concerns sensitive code accidentally committed to a Git repository, this commit warranted detailed examination.

---

# 8. Suspicious Commit Analysis

The suspicious commit was inspected using:

```bash
git show c56c470
```

This command was used to examine the exact changes introduced by the commit.

The investigation focused on:

* Files modified by the commit
* Newly added content
* Removed content
* Changes to source code
* Hardcoded sensitive information
* Challenge-related information
* Evidence explaining why the commit was considered suspicious

The commit represented the key finding during the initial repository analysis.

---

# 9. Evidence

### Repository

```text
/home/ubuntu/commited/commited
```

### Suspicious Commit

```text
c56c470 Oops
```

### Commands Used

```bash
cd /home/ubuntu/commited
ls -la
unzip -l commited.zip
unzip commited.zip
cd commited
git status
git branch -a
git log --all --oneline --decorate --graph
git log --all --stat
ls -la
cat Readme.md
cat main.py
git show c56c470
```

---

# 10. Finding

## Finding: Sensitive Information Potentially Exposed Through Git History

**Severity:** Medium/High
**Category:** Information Disclosure / Sensitive Data Exposure
**Affected Component:** Git Repository History

### Description

The repository contained a suspicious historical commit:

```text
c56c470 Oops
```

The commit was identified during systematic Git history analysis and subsequently examined using `git show`.

The finding demonstrates the security risk associated with committing sensitive information to Git. Information removed from the current working tree may remain accessible through previous commits.

### Security Impact

If sensitive information such as credentials, API keys, tokens, passwords, or confidential source code is committed to a Git repository, simply deleting the information from the latest version does not necessarily remove it from the repository's history.

Anyone with access to the repository may potentially retrieve historical versions of the affected files.

---

# 11. Risk Assessment

| Risk                               | Rating           |
| ---------------------------------- | ---------------- |
| Sensitive information committed    | High             |
| Historical information recoverable | High             |
| Current working tree exposure      | To be determined |
| Credential exposure                | To be determined |
| Repository history exposure        | Confirmed        |
| Overall finding                    | High             |

The final severity depends on the exact sensitive information revealed by commit `c56c470`.

---

# 12. Recommendations

To prevent similar incidents:

### 1. Never commit secrets

Credentials, API keys, passwords, private keys, and other secrets should never be committed directly to source control.

### 2. Use environment variables

Sensitive configuration should be stored outside the source code and supplied through environment variables or an appropriate secrets-management system.

### 3. Configure `.gitignore`

Sensitive local files should be excluded from version control where appropriate.

Example:

```text
.env
*.key
*.pem
secrets.*
credentials.*
```

### 4. Use secret scanning

Repositories should be scanned automatically for accidentally committed credentials and secrets.

### 5. Rotate exposed credentials

If a secret has been committed, removing it from the latest commit is insufficient. Any exposed credential should be considered compromised and rotated immediately.

### 6. Review Git history

Security incidents involving Git repositories should include historical analysis because sensitive data may persist in previous commits.

### 7. Implement pre-commit controls

Automated checks can prevent known secret patterns from being committed in the first place.

---

# 13. Conclusion

The assessment successfully established and analyzed the provided Git repository.

The investigation progressed from basic filesystem enumeration to Git-specific analysis. Branches and commit history were reviewed, current source files were inspected, and a suspicious historical commit was identified:

```text
c56c470 Oops
```

The commit was subsequently examined using `git show`, making it the primary artifact for identifying the accidentally committed sensitive information.

The assessment demonstrates that **Git history must be considered during source-code security investigations**, as information removed from the current version may remain recoverable from historical commits.

---

## 14. Final Testing Status

| Phase                          | Status                         |
| ------------------------------ | ------------------------------ |
| Locate challenge files         | ✅ Completed                    |
| Inspect ZIP                    | ✅ Completed                    |
| Extract repository             | ✅ Completed                    |
| Verify Git repository          | ✅ Completed                    |
| Enumerate branches             | ✅ Completed                    |
| Analyze commit history         | ✅ Completed                    |
| Inspect current files          | ✅ Completed                    |
| Identify suspicious commit     | ✅ Completed                    |
| Inspect `c56c470`              | ✅ Completed                    |
| Identify committed secret/flag | 🔎 Based on `git show c56c470` |
| Document findings              | ✅ Completed                    |
