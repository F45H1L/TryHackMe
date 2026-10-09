# Planning Document — Bugged

### Challenge Link: https://tryhackme.com/room/bugged

## 1. Project Overview

**Project Name:** Bugged — IoT Network Investigation
**Platform:** TryHackMe
**Category:** Network Security, IoT Security, MQTT Analysis
**Environment:** Kali Linux
**Status:** Planned — Not Started

### Challenge Description

John enjoys living in a highly connected environment. While working on his smart-home appliances, he notices unusual network traffic and suspects that something may be wrong.

The objective is to investigate the suspicious network communications, identify the services and protocols involved, determine the source and purpose of the unusual activity, and retrieve the challenge flag.

## 2. Objectives

The primary objectives of this investigation are:

1. Identify active services on the target machine.
2. Discover the protocols used for smart-home device communication.
3. Investigate potentially exposed or misconfigured network services.
4. Analyze message formats and identify unusual or encoded data.
5. Determine whether unauthorized commands or control mechanisms are exposed.
6. Retrieve the challenge flag using evidence gathered during the investigation.
7. Document findings, commands, and security recommendations.

## 3. Scope and Authorization

### In Scope

* The target machine assigned by the TryHackMe room.
* Service and port enumeration.
* Investigation of relevant network protocols.
* MQTT topic and message analysis, if applicable.
* Examination of encoded payloads and suspicious communications.
* Validation of suspected vulnerabilities within the assigned lab environment.

### Out of Scope

* Scanning unrelated machines or networks.
* Attacking external systems.
* Disrupting services beyond what is necessary for the challenge.
* Reusing discovered credentials or access against systems outside the lab.

All testing will remain within the authorized TryHackMe environment.

## 4. Initial Hypotheses

Before gathering evidence, the following possibilities will be considered:

* A network service may be exposed without sufficient authentication.
* Smart-home devices may communicate through an IoT messaging protocol.
* Some network messages may contain encoded configuration data.
* A device may expose an undocumented command interface.
* Misconfigured access controls may allow unauthorized observation or interaction with devices.

These are hypotheses only. Each must be tested and supported by evidence before being treated as a finding.

## 5. Tools and Resources

| Tool                         | Planned Purpose                                     |
| ---------------------------- | --------------------------------------------------- |
| Nmap                         | Discover open ports and identify services           |
| Mosquitto Clients            | Subscribe to and publish MQTT messages              |
| Wireshark                    | Inspect network packets and communication patterns  |
| TShark                       | Analyze packet captures from the terminal           |
| Base64 utilities             | Decode potentially encoded payloads                 |
| Linux command-line utilities | Inspect output, process data, and document findings |
| TryHackMe                    | Provide the authorized target environment           |

Tools will be selected based on the services and protocols discovered during reconnaissance.

## 6. Investigation Methodology

### Phase 1 — Environment Preparation

**Objective:** Prepare the testing environment and identify the assigned target.

Planned activities:

* Start the TryHackMe room and establish the required lab connection.
* Identify the target IP address.
* Confirm that the target is reachable.
* Ensure the required tools are available in Kali Linux.
* Create a directory for notes and collected evidence.

Example preparation commands:

```bash
mkdir -p ~/tryhackme/bugged/evidence
cd ~/tryhackme/bugged
```

Record the target IP, date, tool versions, and any relevant lab instructions.

### Phase 2 — Network Reconnaissance

**Objective:** Identify exposed ports and services.

Planned activities:

* Perform an initial connectivity check.
* Scan TCP ports.
* Identify service versions on discovered ports.
* Record interesting services for further investigation.

Example command:

```bash
nmap -sV -p- <TARGET_IP> -oN evidence/nmap-scan.txt
```

**Expected output:** A list of open ports and identified services.

**Decision point:** Select the next investigation steps based on the services discovered.

### Phase 3 — Protocol Identification

**Objective:** Understand how the target communicates with connected devices.

Planned activities:

* Identify services associated with IoT messaging.
* Determine whether MQTT or another relevant protocol is in use.
* Examine service behavior and authentication requirements.
* Use Wireshark or TShark if packet-level analysis is necessary.

Example MQTT subscription command, if port 1883 is identified as an MQTT service:

```bash
mosquitto_sub -h <TARGET_IP> -p 1883 -t '#' -v
```

This command attempts to subscribe to all MQTT topics. Access may be denied if authentication or authorization is required.

### Phase 4 — Message and Payload Analysis

**Objective:** Investigate unusual messages and identify potentially sensitive information.

Planned activities:

* Record topic names and message contents.
* Identify recurring device messages and unusual topics.
* Inspect payload structure, including JSON or binary data.
* Test whether suspicious payloads use common encoding schemes.
* Decode data only when its format supports that conclusion.
* Document any identifiers, configuration fields, or additional communication topics discovered.

Example Base64 decoding command:

```bash
echo '<ENCODED_PAYLOAD>' | base64 -d
```

Decoded data will be treated as untrusted evidence. Any commands or instructions found within it will be evaluated before use.

### Phase 5 — Vulnerability Investigation

**Objective:** Determine whether the observed communications reveal an exploitable security weakness.

Planned activities:

* Check whether the messaging service permits unauthenticated access.
* Investigate access controls for relevant topics.
* Determine whether exposed messages reveal internal configuration.
* Assess whether a device accepts commands from unauthorized clients.
* Validate any suspected weakness using controlled tests within the assigned lab.
* Avoid destructive actions and unnecessary privilege escalation.

Each potential finding should include the observed behavior, reproduction steps, impact, and supporting evidence.

### Phase 6 — Flag Retrieval

**Objective:** Retrieve the challenge flag through the intended investigation path.

Planned activities:

* Use the evidence gathered during earlier phases to identify the relevant device or interface.
* Determine which interactions are supported by the service.
* Investigate accessible files or responses only when justified by observed behavior.
* Retrieve the flag within the authorized environment.
* Verify the result against the TryHackMe challenge interface.

The exact retrieval method will remain undetermined until the investigation provides sufficient evidence.

### Phase 7 — Documentation and Reporting

**Objective:** Produce a clear, reproducible record of the investigation.

The final report will include:

* Challenge overview and objectives.
* Tools and environment details.
* Reconnaissance results.
* Relevant services and protocols.
* Evidence of suspicious communications.
* Analysis of any identified vulnerability.
* Reproduction steps.
* Flag retrieval outcome.
* Security recommendations.
* Lessons learned.

## 7. Evidence Collection Plan

Evidence will be stored under the `evidence/` directory.

| Evidence ID | Planned Evidence                          | Purpose                                   |
| ----------- | ----------------------------------------- | ----------------------------------------- |
| E-01        | Nmap scan output                          | Record exposed ports and services         |
| E-02        | MQTT topic and message output             | Identify device communication patterns    |
| E-03        | Relevant packet capture, if available     | Preserve network-level evidence           |
| E-04        | Decoded configuration data, if discovered | Document protocol or device configuration |
| E-05        | Service responses to controlled tests     | Validate suspected behavior               |
| E-06        | Flag verification result                  | Confirm challenge completion              |

Sensitive information will not be published unnecessarily. Any evidence shared publicly will be reviewed for credentials, tokens, or other secrets.

## 8. Risk Assessment

| Potential Risk                             | Mitigation                                               |
| ------------------------------------------ | -------------------------------------------------------- |
| Accidental interaction with the wrong host | Verify the assigned target IP before testing             |
| Disruption of smart-home services          | Prefer passive observation and harmless test commands    |
| Exposure of sensitive data                 | Store evidence carefully and redact secrets              |
| Misinterpretation of encoded data          | Preserve original payloads and verify decoding           |
| Unintended command execution               | Validate command formats and arguments before publishing |
| Temporary lab IP changes                   | Confirm the current target IP after restarting the room  |

## 9. Success Criteria

The investigation will be considered complete when:

* [ ] The target's exposed services have been identified.
* [ ] Relevant network protocols have been investigated.
* [ ] Suspicious communications have been analyzed.
* [ ] Any identified vulnerability has been validated.
* [ ] The challenge flag has been retrieved and accepted.
* [ ] The methodology and findings have been documented.
* [ ] Appropriate security recommendations have been recorded.

## 10. Expected Learning Outcomes

By completing this challenge, the investigation aims to improve understanding of:

* Network reconnaissance and service enumeration.
* IoT communication protocols.
* MQTT topics, subscriptions, and message publishing.
* Analysis of encoded network payloads.
* Authentication and authorization weaknesses.
* Evidence-based vulnerability investigation.
* Security reporting and technical documentation.

## 11. Final Notes

This document defines the investigation plan before testing begins. No vulnerability, exposed service, backdoor, or flag retrieval method is assumed to exist until it is verified during the challenge.

The plan may be updated as new evidence is collected. Any changes should be supported by observed results and documented in the final report.

**Current Status:** Planned — Awaiting initial reconnaissance.