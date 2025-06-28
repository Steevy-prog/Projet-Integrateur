import os

hostname = "google.com"  # or an IP like "192.168.1.1"
response = os.system(f"ping -c 1 {hostname}")

if response == 0:
    print(f"{hostname} is reachable ✅")
    # do something
else:
    print(f"{hostname} is unreachable ❌")
    # do something else