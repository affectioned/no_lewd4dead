import subprocess
import re
import os
from playwright.sync_api import sync_playwright

BLOCKED_IPS_FILE = "blocked_ips.txt"
DUMPED_IPS_FILE = "dumped_ips.txt"

# List of SourceBans URLs
SOURCEBANS_URLS = [
    "https://sb.hitoha.moe/index.php?p=servers&s=0",
    "https://www.lewd4dead-elite.com/sb/index.php?p=servers&s=0"
]

def get_server_ips():
    """
    Uses Playwright to extract **actual server IPs** from multiple SourceBans pages, 
    and strips the port numbers.
    """
    try:
        all_ip_addresses = set()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for sourceban_url in SOURCEBANS_URLS:
                print(f"Fetching data from: {sourceban_url}")

                # ✅ Navigate to the URL and wait for full load
                response = page.goto(
                    sourceban_url, wait_until="networkidle", timeout=60000
                )

                if not response or response.status != 200:
                    print(f"Failed to load page {sourceban_url}, status code: {response.status if response else 'No Response'}")
                    continue

                # ✅ Extract the text content of the page (ignoring HTML tags)
                page_text = page.inner_text("body")

                # ✅ Use regex to find all IPv4 addresses
                matches = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", page_text)
                
                # ✅ Add all matches to the set
                all_ip_addresses.update(matches)

                print(f"Found {len(matches)} IPs from {sourceban_url}")

            browser.close()

        return all_ip_addresses

    except Exception as e:
        print(f"Error fetching data: {e}")
        return set()
    
def block_ip(ip):
    command = f"netsh advfirewall firewall add rule name=\"Block {ip} LEWD4DEAD2\" dir=in action=block remoteip={ip}"
    subprocess.run(command, shell=True)
    print(f"Blocked IP: {ip}")

def get_existing_blocked_ips():
    command = [
        "powershell", "-Command",
        "Get-NetFirewallRule | Where-Object {$_.DisplayName -like 'Block L4D2 Server *'} | Select-Object -ExpandProperty RemoteAddress"
    ]
    result = subprocess.run(command, shell=True,
                            capture_output=True, text=True)
    return set(result.stdout.split())

def load_blocked_ips():
    if not os.path.exists(BLOCKED_IPS_FILE):
        return set()
    with open(BLOCKED_IPS_FILE, "r") as file:
        return set(line.strip() for line in file.readlines())


def load_dumped_ips():
    if not os.path.exists(DUMPED_IPS_FILE):
        return set()
    with open(DUMPED_IPS_FILE, "r") as file:
        return set(line.strip() for line in file.readlines())

def block_malicious_ips():
    print("Fetching server IP addresses from SourceBans...")
    server_ips = get_server_ips()

    if not server_ips:
        print("No Server IPs found on SourceBans")
        return

    existing_ips = load_blocked_ips()
    new_ips = server_ips - existing_ips

    if not new_ips:
        print("No new IPs to block. All known server IPs are already dumped.")
        return

    print(f"Blocking {len(new_ips)} IPs...")
    for ip in new_ips:
        block_ip(ip)

    if os.path.isfile(BLOCKED_IPS_FILE):
        os.remove(BLOCKED_IPS_FILE)

    # Save to file
    with open(BLOCKED_IPS_FILE, "w") as file:
        for ip in sorted(server_ips):
            file.write(ip + "\n")

    print(f"\nServer IPs have been saved to {BLOCKED_IPS_FILE}.")

def unblock_all_ips():
    blocked_ips = load_blocked_ips()

    if not blocked_ips:
        print("No blocked IPs found in file.")
        return

    print(f"Unblocking {len(blocked_ips)} IPs...")
    for ip in blocked_ips:
        #unblock_ip(ip)
        print(f"Unblocked {ip}")

    os.remove(BLOCKED_IPS_FILE)
    print("All blocked IPs have been removed and file deleted.")

def dump_all_ips():
    print("Fetching server IP addresses from SourceBans...")
    server_ips = get_server_ips()

    if not server_ips:
        print("No Server IPs found on SourceBans")
        return

    existing_ips = load_dumped_ips()
    new_ips = server_ips - existing_ips

    if not new_ips:
        print("No new IPs to block. All known server IPs are already dumped.")
        return

    print("\nServer IPs:")
    for ip in sorted(server_ips):
        print(ip)

    if os.path.isfile(DUMPED_IPS_FILE):
        os.remove(DUMPED_IPS_FILE)

    # Save to file
    with open(DUMPED_IPS_FILE, "w") as file:
        for ip in sorted(server_ips):
            file.write(ip + "\n")

    print(f"\nServer IPs have been saved to {DUMPED_IPS_FILE}.")

def main():
    while True:
        print("\nL4D2 Malicious Server Blocker")
        print("1. Block malicious IPs")
        print("2. Unblock all IPs")
        print("3. Dump all IPs")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            block_malicious_ips()
        elif choice == "2":
            unblock_all_ips()
        elif choice == "3":
            dump_all_ips()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
