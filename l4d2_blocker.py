import subprocess
import ctypes
import re
import os
from playwright.sync_api import sync_playwright

BLOCKED_IPS_FILE = "blocked_ips.txt"
DUMPED_IPS_FILE = "dumped_ips.txt"

SOURCEBANS_URLS = [
    "https://sb.hitoha.moe/index.php?p=servers&s=0",
    "https://www.lewd4dead-elite.com/sb/index.php?p=servers&s=0"
]

def get_server_ips():
    try:
        all_ip_addresses = set()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for sourceban_url in SOURCEBANS_URLS:
                print(f"Fetching data from: {sourceban_url}")

                try:
                    response = page.goto(sourceban_url, wait_until="networkidle", timeout=60000)

                    if not response or response.status != 200:
                        print(f"Failed to load page {sourceban_url}, status: {response.status if response else 'No Response'}")
                        continue

                    matches = set(re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", page.inner_text("body")))
                    print(f"Found {len(matches)} IPs from {sourceban_url}")

                    all_ip_addresses.update(matches)
                
                except Exception as e:
                    print(f"Error processing {sourceban_url}: {e}")

            browser.close()

        return all_ip_addresses

    except Exception as e:
        print(f"Error fetching data: {e}")
        return set()

def block_ip(ip):
    try:
        command = f"netsh advfirewall firewall add rule name=\"Block {ip} LEWD4DEAD2\" dir=in action=block remoteip={ip}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Blocked IP: {ip}")
        else:
            print(f"Failed to block {ip}. Error: {result.stderr.strip()}")
    
    except Exception as e:
        print(f"Error blocking {ip}: {e}")

def save_ips_to_file(filename, ip_set):
    existing_ips = load_ips_from_file(filename)

    new_ips = ip_set - existing_ips
    if not new_ips:
        print(f"No new IPs to add to {filename}.")
        return

    with open(filename, "a") as file:
        for ip in sorted(new_ips):
            file.write(ip + "\n")

    print(f"{len(new_ips)} new IPs added to {filename}.")

def load_ips_from_file(filename):
    if not os.path.exists(filename):
        return set()

    with open(filename, "r") as file:
        return set(line.strip() for line in file.readlines())

def unblock_ip(ip):
    try:
        command = f"netsh advfirewall firewall delete rule name=\"Block {ip} LEWD4DEAD2\" remoteip={ip}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Unblocked {ip}")
        else:
            print(f"Failed to unblock {ip}. Error: {result.stderr.strip()}")
    
    except Exception as e:
        print(f"Error unblocking {ip}: {e}")

def block_all_ips():
    server_ips = get_server_ips()

    if not server_ips:
        print("No server IPs found on SourceBans.")
        return
    
    print(f"Blocking {len(server_ips)} IPs...")
    for ip in server_ips:
        block_ip(ip)

    os.remove(BLOCKED_IPS_FILE)
    save_ips_to_file("blocked_ips.txt", server_ips)

def unblock_all_ips():
    blocked_ips = load_ips_from_file(BLOCKED_IPS_FILE)

    if not blocked_ips:
        print("No blocked IPs found.")
        return

    print(f"Unblocking {len(blocked_ips)} IPs...")
    for ip in blocked_ips:
        unblock_ip(ip)

    os.remove(BLOCKED_IPS_FILE)
    print("All blocked IPs have been removed.")

def dump_all_ips():
    server_ips = get_server_ips()

    if not server_ips:
        print("No server IPs found on SourceBans.")
        return
    
    os.remove(DUMPED_IPS_FILE)
    save_ips_to_file("dumped_ips.txt", server_ips)

def main():
    while True:
        print("\nL4D2 Malicious Server Blocker")
        print("1. Block malicious IPs")
        print("2. Unblock all IPs")
        print("3. Dump all IPs")
        print("4. Exit")
        print("---------------")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("This script must be run as an administrator for Windows Firewall Settings.")
                exit
            block_all_ips()
        elif choice == "2":
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("This script must be run as an administrator for Windows Firewall Settings.")
                exit
            unblock_all_ips()
        elif choice == "3":
            dump_all_ips()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()