### **No Lewd4Dead**  

This script blocks or unblocks Left 4 Dead 2 (L4D2) servers that contain "Lewd4Dead" in their name. It uses PowerShell’s Windows Firewall rules to block unwanted servers and keeps a log of blocked IPs in `blocked_ips.txt`.  

---

## **Installation**  

1. **Install Python** (if not already installed)  
   - Download and install Python 3.x from [Python.org](https://www.python.org/downloads/)  
   - Ensure pip is installed (comes with Python 3.x)  

2. **Install dependencies**  
   Open a terminal (Command Prompt or PowerShell) and run:  
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** and add your Steam API key:  
   - Get a Steam API key from [Steam Developer](https://steamcommunity.com/dev/apikey)  
   - Create a new `.env` file in the same folder as `l4d2_blocker.py`  
   - Add this line (replace `YOUR_API_KEY` with your actual key):  
     ```
     STEAM_API_KEY=YOUR_API_KEY
     ```

---

## **How to Run**  

1. **Run as Administrator**  
   The script modifies firewall rules, so it must be run with admin privileges.  
   - Open Command Prompt (Admin) or PowerShell (Admin).  
   - Navigate to the script directory:  
     ```bash
     cd path\to\script
     ```
   - Run the script:  
     ```bash
     python l4d2_blocker.py
     ```

2. **Choose an option:**  
   ```
   Choose an option:
   [1] Block servers
   [2] Unblock all servers
   > 
   ```
   - Enter `1` to scan and block servers.  
   - Enter `2` to remove all firewall blocks from `blocked_ips.txt`.  
