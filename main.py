import os
import requests
import subprocess
import sys
import ctypes
from dotenv import load_dotenv

BLOCKLIST_FILE = "blocked_ips.txt"
blocked_ips = {}  # Dictionary to track blocked IPs and prevent duplicates

def is_admin():
    """Check if the script is running as Administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def sanitize_ip(ip_with_port):
    """Extract the IP address without the port."""
    return ip_with_port.split(":")[0]

def block_ip(ip, name):
    """Block an IP using PowerShell's New-NetFirewallRule."""
    if not is_admin():
        print("❌ Error: This script must be run as Administrator to modify firewall rules.")
        return False

    # Skip if the IP is already blocked
    if ip in blocked_ips:
        print(f"⏩ Skipping already blocked IP: {ip}")
        return False

    command = [
        "powershell", "-Command",
        f"New-NetFirewallRule -DisplayName 'Block {ip} LEWD4DEAD2' -Direction Inbound -Action Block -RemoteAddress {ip}"
    ]

    try:
        print(f"🔧 Blocking: {ip} | {name}")
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Blocked IP: {ip} | {name}")
            blocked_ips[ip] = name  # Mark as blocked
            return True
        else:
            error_message = result.stderr.strip()
            if not error_message:
                error_message = "Unknown error (empty response from PowerShell)"
            print(f"❌ Failed to block {ip}. Error: {error_message}")
            return False

    except Exception as e:
        print(f"⚠️ Exception while blocking {ip}: {e}")
        return False

def unblock_all():
    """Unblock all previously blocked IPs listed in blocked_ips.txt."""
    if not is_admin():
        print("❌ Error: This script must be run as Administrator to modify firewall rules.")
        return

    if not os.path.exists(BLOCKLIST_FILE):
        print("🚫 No blocked IPs found in blocked_ips.txt.")
        return

    with open(BLOCKLIST_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        print("🚫 No blocked IPs found in blocked_ips.txt.")
        return

    for line in lines:
        parts = line.strip().split(" | ")
        if len(parts) < 1:
            continue

        ip = sanitize_ip(parts[0])  # Remove port if present

        command = [
            "powershell", "-Command",
            f"Remove-NetFirewallRule -DisplayName 'Block {ip} LEWD4DEAD2'"
        ]

        try:
            print(f"🔄 Unblocking: {ip}")
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Unblocked IP: {ip}")
            else:
                error_message = result.stderr.strip()
                if not error_message:
                    error_message = "Unknown error (empty response from PowerShell)"
                print(f"❌ Failed to unblock {ip}. Error: {error_message}")

        except Exception as e:
            print(f"⚠️ Exception while unblocking {ip}: {e}")

    os.remove(BLOCKLIST_FILE)  # Delete the file after unblocking all
    print("🗑️ All blocked IPs have been removed.")

# Load .env file
load_dotenv()

# Get Steam API Key from .env
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
if not STEAM_API_KEY:
    raise ValueError("STEAM_API_KEY is missing from .env file!")

# Load already blocked IPs from file to avoid rebanning them
if os.path.exists(BLOCKLIST_FILE):
    with open(BLOCKLIST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" | ")
            if len(parts) >= 2:
                blocked_ips[sanitize_ip(parts[0])] = parts[1]

# User choice: Block or Unblock?
print("\n📌 Choose an option:")
print("[1] Block servers")
print("[2] Unblock all servers")
choice = input("> ")

if choice == "2":
    unblock_all()
    sys.exit(0)

elif choice != "1":
    print("❌ Invalid choice. Exiting.")
    sys.exit(1)

# Steam Web API endpoint for fetching L4D2 servers
BASE_URL = "https://api.steampowered.com/IGameServersService/GetServerList/v1/"
FILTER = "\\appid\\550"
LIMIT = 10000  # Max number of servers per request

last_ip = None  # Used for pagination
newly_blocked = []  # Track newly blocked IPs

while True:
    # Construct API URL with pagination
    params = {
        "key": STEAM_API_KEY,
        "filter": FILTER,
        "limit": LIMIT,
    }
    if last_ip:
        params["last_ip"] = last_ip  # Request next batch of servers

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        servers = data.get('response', {}).get('servers', [])

        if not servers:
            print("No more servers available.")
            break  # Stop if no more servers are returned

        print(f"Fetched {len(servers)} more servers.")

        # Check if any server in the batch needs to be blocked
        batch_blocked = False
        for server in servers:
            ip_with_port = server["addr"]  # IP format: "192.168.1.1:27015"
            name = server["name"]
            clean_ip = sanitize_ip(ip_with_port)

            if "Lewd4Dead" in name and clean_ip not in blocked_ips:
                batch_blocked = True
                if block_ip(clean_ip, name):
                    newly_blocked.append(f"{clean_ip} | {name}")

        # Update last_ip for the next query
        last_ip = servers[-1]["addr"]

        # Stop querying if the last batch had **zero matches**
        if not batch_blocked:
            print("No matching servers found in this batch. Stopping.")
            break

    else:
        print("Failed to fetch server list.")
        break

# Save newly blocked IPs to the file
if newly_blocked:
    with open(BLOCKLIST_FILE, "a", encoding="utf-8") as f:  # Append mode to avoid overwriting old entries
        f.write("\n".join(newly_blocked) + "\n")
    print(f"Blocked IPs saved to {BLOCKLIST_FILE}")
else:
    print("No new servers matched the blocking criteria.")