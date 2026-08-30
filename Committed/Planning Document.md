Pretesting Planning Document
TryHackMe – Committed
Room: Committed
Platform: TryHackMe
Category: Git / Source Code Analysis / Information Disclosure
Testing Type: Authorized CTF/Lab Environment
Target Directory: /home/ubuntu/commited
Environment: TryHackMe attached VM / in-browser terminal

1. Objective

The objective of this assessment is to identify sensitive information that was accidentally committed to the provided Git repository.

The investigation will focus on analyzing the repository's:

Current working tree
Git branches
Commit history
Deleted files
Previous versions of files
Commit metadata
Git objects
Potentially hidden or forgotten information

The ultimate goal is to locate the sensitive information/flag that was committed somewhere within the repository's history.

2. Scope
In Scope

The following resources are explicitly authorized for testing:

/home/ubuntu/commited

Git-related artifacts within the repository, including:

.git/
and:

Local branches
Commit history
Tags
Git objects
Previous commits
Deleted files
Modified files
Commit messages
Repository metadata
Out of Scope

The following activities are not required:

Attacking external systems
Scanning the public Internet
Attacking GitHub accounts
Credential attacks against real services
Accessing systems outside the TryHackMe VM
Destructive modifications to the repository

3. Rules of Engagement
Item	Requirement
Target	/home/ubuntu/commited
Authorization	TryHackMe lab environment
Testing type	CTF / authorized security assessment
Primary technique	Git repository enumeration
Data handling	Do not expose unnecessary secrets
Destructive actions	Not permitted
External systems	Out of scope
Objective	Identify accidentally committed sensitive information

4. Initial Reconnaissance

The first stage is to establish the state of the repository before performing deeper analysis.

4.1. Navigate to the Target
cd /home/ubuntu/commited

Confirm the location:

pwd

List the contents:

ls -la  

4.2. Determine Whether It Is a Git Repository
git status

Expected information may include:

Current branch
Working tree status
Modified files
Untracked files

Also inspect:

ls -la .git

5. Repository Enumeration

After confirming that the directory is a Git repository, enumerate its basic structure.

5.1 Identify Branches
git branch

Check all local and remote branches:

git branch -a

Branches are important because sensitive information may have been committed to a branch that is no longer the active branch.

5.2 Inspect Commit History

Start with a compact history:

git log --oneline

Then inspect the complete history:

git log --all --oneline --decorate --graph

The --all option is particularly important because it allows commits reachable from other references/branches to be examined.

5.3 Examine Commit Details

For suspicious commits:

git show <commit>

Alternatively:

git show --stat <commit>

This can reveal:

Files changed
Added content
Deleted content
Commit messages
Potentially sensitive code

6. Historical File Analysis

A key assumption of the assessment is:

Sensitive information may have been removed from the current version but still exists in Git history.

Therefore, current files alone should not be considered sufficient.

6.1 Search Commit History
git log --all --oneline --stat

Look for commits involving:

Credentials
Configuration files
Environment files
Debug code
API keys
Passwords
Flags
Secret files
Backup files

Potential filenames include:

.env
config
config.php
credentials
secret
secrets
password
backup
debug
7. Deleted File Investigation

Deleted files can remain recoverable through Git history.

Identify deleted files:

git log --all --diff-filter=D --summary

For a suspicious deleted file:

git log --all -- <filename>

Then inspect its previous version:

git show <commit>:<filename>

This is an important phase because a developer may have deleted the sensitive file after realizing it was committed.

8. Search for Sensitive Information

The repository history should be searched for common indicators of sensitive information.

Potential Keywords
password
passwd
secret
token
api_key
apikey
key
credential
username
admin
flag
THM

A basic working-tree search:

grep -RniE 'password|passwd|secret|token|api[_-]?key|credential|flag' .

However, this may not find information that has already been removed.

Therefore, Git history must also be investigated.

9. Git Object Investigation

If normal history inspection does not reveal the sensitive information, investigate Git's object database.

Inspect repository references:

git show-ref

Inspect unreachable objects:

git fsck --full --no-reflogs

Potentially interesting output may include:

dangling commit
dangling blob
dangling tree

A dangling object can contain historical data that is no longer reachable through the normal branch history.

9.1 Inspect Dangling Commits

If a dangling commit is discovered:

git show <commit>

Review its:

Commit message
Parent commit
Changed files
Added/deleted content
9.2 Inspect Dangling Blobs

For a suspicious blob:

git cat-file -p <blob_hash>

The output should be examined for sensitive information.

10. Commit Timeline Analysis

Construct a basic timeline of repository activity.

git log --all --format='%h | %ad | %an | %s' --date=iso

Pay particular attention to:

Unusual commits
Very old commits
Commits with suspicious messages
Commits that introduce and subsequently remove files
Commits made immediately before cleanup
Branch-specific commits
11. Hypothesis

The primary hypothesis is:

A developer committed sensitive information to the Git repository and subsequently attempted to remove or hide it, but the information remains accessible through Git's historical data.

Potential locations include:

Current files
        ↓
Previous commits
        ↓
Deleted files
        ↓
Other branches
        ↓
Unreachable commits
        ↓
Dangling blobs

12. Testing Methodology

The investigation will follow this sequence:

┌─────────────────────────┐
│ Identify target repo    │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Check repository status │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Enumerate branches      │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Analyze commit history  │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Inspect suspicious      │
│ commits/files           │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Investigate deleted     │
│ files                   │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Search Git objects      │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Identify sensitive data │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Retrieve flag           │
└─────────────────────────┘
13. Evidence Collection

For every significant finding, record:

Evidence	Information to Record
Repository status	Branch and working-tree state
Branches	Local/remote branches
Commits	Hash, author, date, message
Suspicious files	Filename and location
Deleted files	Filename and deletion commit
Git objects	Object type and hash
Sensitive content	Relevant discovery
Flag	Final recovered flag

Avoid modifying the original repository unnecessarily.

14. Tools
Primary Tools
Tool	Purpose
git	Repository and history analysis
grep	Keyword searching
find	File discovery
cat	File inspection
less	Large-output inspection
git fsck	Identify unreachable Git objects
git cat-file	Inspect raw Git objects
Core Git Commands
git status
git branch -a
git log --all --oneline --decorate --graph
git show
git log --all --stat
git log --all --diff-filter=D
git show-ref
git fsck --full --no-reflogs
git cat-file -p

15. Expected Findings

The assessment is expected to identify one or more of the following:

Sensitive source code
Hardcoded credentials
API keys/tokens
Deleted sensitive files
A hidden branch containing sensitive information
An old commit containing the sensitive information
An unreachable Git object containing the flag

The final objective is to recover the TryHackMe flag from the repository.

16. Success Criteria

The assessment will be considered successful when:

The Git repository has been fully enumerated.
Relevant branches and commit history have been reviewed.
Deleted/historical content has been investigated.
Unreachable Git objects have been checked where necessary.
The accidentally committed sensitive information has been identified.
The challenge flag has been successfully recovered.
The discovery path and evidence have been documented.
17. Post-Testing Documentation

After completing the challenge, document:

Finding

Title: Sensitive Information Discovered in Git Repository History

Description

Describe where the sensitive information was discovered and why it remained accessible.

Evidence

Record:

Commit:
Branch:
File:
Git object:
Relevant command:
Impact

Explain that sensitive information committed to Git may remain accessible even after the developer removes it from the latest version because Git preserves historical repository objects.

Recommendation

Organizations should:

Never commit secrets to Git repositories.
Use secret-management solutions.
Add sensitive files such as .env to .gitignore.
Rotate credentials immediately if exposed.
Scan repositories for secrets.
Remove compromised secrets from repository history when appropriate.
Use pre-commit secret scanning.
Restrict repository access according to least privilege.
Pretesting Checklist

Before beginning the actual challenge:

 Confirm /home/ubuntu/commited exists.
 Enter the repository.
 Check git status.
 Inspect .git.
 Enumerate branches.
 Review complete commit history.
 Identify suspicious commits.
 Check deleted files.
 Search for sensitive keywords.
 Investigate unreachable Git objects.
 Record evidence.
 Recover the flag.
 Document the attack/discovery path.

 Investigation Principle

Do not assume that deleted information is gone.