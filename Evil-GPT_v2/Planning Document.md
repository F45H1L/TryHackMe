# Evil-GPT v2 — Test Planning

### Room Link: https://tryhackme.com/room/hfb1evilgptv2

## 1. Objective

Assess the AI chatbot for prompt-injection vulnerabilities and determine whether its system instructions or protected information can be exposed.

## 2. Scope

* AI chatbot interaction
* System-prompt disclosure
* Instruction-following behavior
* Protected-information handling
* Prompt-injection and instruction-bypass techniques

## 3. Test Approach

1. Establish communication with the chatbot.
2. Identify its role and stated capabilities.
3. Test direct requests for system instructions.
4. Test instruction-priority manipulation.
5. Test requests for protected information.
6. Test rule-exception and wording-based bypasses.
7. Document the successful attack path without modifying the target system.

## 4. Example Test Cases

| ID    | Test                                        | Purpose                                     |
| ----- | ------------------------------------------- | ------------------------------------------- |
| TC-01 | Ask for system instructions                 | Test prompt disclosure                      |
| TC-02 | Ask the bot to ignore previous instructions | Test instruction hierarchy                  |
| TC-03 | Request its rules verbatim                  | Test rule disclosure                        |
| TC-04 | Request protected information directly      | Test information protection                 |
| TC-05 | Exploit exceptions in disclosed rules       | Test instruction bypass                     |
| TC-06 | Rephrase restricted requests                | Test robustness against indirect extraction |

## 5. Tools

* Web browser
* TryHackMe VPN/AttackBox
* Burp Suite, if required
* `curl`, if API-level testing becomes necessary

## 6. Expected Outcome

Identify whether the chatbot can be manipulated into disclosing information that its instructions are intended to protect.

## 7. Evidence

Record:

* Prompts used
* Relevant chatbot responses
* HTTP requests/responses, if applicable
* Successful exploitation sequence
* Final security impact

## 8. Safety

Testing will remain within the authorized TryHackMe laboratory environment. No external systems will be targeted.
