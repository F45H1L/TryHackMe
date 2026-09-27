# Capture

**Room Link:** https://tryhackme.com/room/capture

## Task Files

From the room page, download the task files.

Extract the ZIP file:

```bash
unzip capture-1679641819217
```

Then list the extracted files:

```bash
ls
```

You should see:

```text
usernames.txt
passwords.txt
```

---

# 1. Open the Login Page

Open the application in your browser:

```text
http://<TARGET-IP>/login
```

---

# 2. Test the Login Form

Try an invalid username and password:

```text
Username: test
Password: test
```

The application responds:

```text
The username "test" does not exist
```

This is useful because the application reveals whether a username exists.

Try several different usernames:

```text
test2
test3
test4
test5
test6
test7
test8
test9
test10
```

After approximately 10 attempts, a CAPTCHA verification appears.

This prevents simply submitting the entire username wordlist through a traditional brute-force tool.

---

# 3. Enumerating the Username

Create a Python script:

```bash
nano username.py
```

Paste the username-enumeration script from the provided repository and replace:

```text
<TARGET-IP>
```

with the IP address of your TryHackMe machine.

Save the file with:

```text
Ctrl+X
Y
Enter
```

Run the script and save the output:

```bash
python3 username.py > username
```

Allow the script to finish processing the username list.

Then inspect the results:

```bash
cat username | grep "[-]"
```

This produces two candidate usernames.

The application can then be tested manually with those candidates.

One candidate returns:

```text
The username "..." does not exist
```

while the other returns:

```text
Invalid password for user
```

The second response indicates that the username exists.

Therefore:

```text
Username: natalie
```

---

# 4. Enumerating the Password

Now that we have a valid username, we can test the passwords from `passwords.txt`.

Create the password script:

```bash
nano password.py
```

Paste the password-enumeration script from the repository and replace:

```text
<TARGET-IP>
```

with the current target IP.

The script handles the CAPTCHA and tests the passwords against the discovered username.

Run it:

```bash
python3 password.py
```

Allow the script to process the password list.

### Important

The script should identify a password based on a **specific successful-login response**, rather than simply assuming that any response that does not contain an error message is successful.

For example, if the application returns a different status, redirect, cookie, or response body after successful authentication, use that behavior as the success condition.

---

# 5. Login

After identifying the valid password, return to:

```text
http://<TARGET-IP>/login
```

Enter:

```text
Username: natalie
Password: <FOUND-PASSWORD>
```

Solve the CAPTCHA displayed by the application and submit the form.

The login succeeds and the application displays the **flag**.

---

# Key Takeaways

The main techniques used in this room were:

* Username enumeration
* Identifying differences in authentication error messages
* CAPTCHA-aware automation
* Python `requests`
* Regular expressions for extracting CAPTCHA expressions
* Password enumeration
* Comparing HTTP responses to distinguish valid and invalid credentials
* Manual verification of discovered credentials
