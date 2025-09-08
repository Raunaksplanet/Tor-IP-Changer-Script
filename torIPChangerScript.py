import os
import subprocess
import sys
import socket
import time
import shutil
import requests
import argparse
from stem import Signal
from stem.control import Controller

TORRC_PATH = "/etc/tor/torrc"

def install_dependencies():
    print("[*] Installing dependencies...")
    subprocess.run(["sudo", "apt", "update", "-y"])
    subprocess.run(["sudo", "apt", "install", "-y", "tor", "python3-pip"])
    
    # Use --break-system-packages for pip installation
    subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "--upgrade", "stem", "requests[socks]"])
    print("[+] Dependencies installed successfully")

def configure_tor():
    print("[*] Configuring Tor...")
    torrc_content = """
SocksPort 9050
ControlPort 9051
CookieAuthentication 0
"""
    try:
        with open("torrc.tmp", "w") as f:
            f.write(torrc_content)
        subprocess.run(["sudo", "mv", "torrc.tmp", TORRC_PATH])
    except Exception as e:
        print(f"[-] Error writing torrc: {e}")
        return

    # Check if Tor is already running
    if is_port_in_use(9050) or is_port_in_use(9051):
        print("[!] Tor already running. Skipping restart.")
        return

    # Try restarting Tor (WSL may not support systemctl)
    if shutil.which("systemctl"):
        # Linux path
        subprocess.run(["sudo", "systemctl", "restart", "tor"])
    elif shutil.which("service"):
        subprocess.run(["sudo", "service", "tor", "restart"])
    else:
        # macOS / Homebrew path
        subprocess.run(["brew", "services", "restart", "tor"])
    time.sleep(3)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def connect_to_tor():
    print("[*] Connecting to Tor controller...")
    try:
        controller = Controller.from_port(port=9051)
        controller.authenticate()
        print("[+] Connected to Tor controller.")
        return controller
    except Exception as e:
        print(f"[-] Could not connect to Tor controller: {e}")
        return None

def renew_identity(controller):
    if controller:
        try:
            print("[*] Requesting new Tor circuit...")
            controller.signal(Signal.NEWNYM)
            time.sleep(3)  # Wait for circuit to rebuild
            print("[+] New identity acquired.")
            return True
        except Exception as e:
            print(f"[-] Error renewing identity: {e}")
            return False
    else:
        print("[-] No Tor controller connected.")
        return False

def get_ip():
    try:
        session = requests.session()
        session.proxies = {"http": "socks5h://127.0.0.1:9050",
                           "https": "socks5h://127.0.0.1:9050"}
        ip = session.get("https://httpbin.org/ip", timeout=10).json()["origin"]
        return ip
    except Exception as e:
        return f"Error fetching IP: {e}"

def continuous_ip_change(interval=10):
    """Continuously change IP every specified interval (seconds)"""
    controller = None
    cycle_count = 0
    
    try:
        controller = connect_to_tor()
        if not controller:
            print("[!] Tor controller unavailable. Exiting.")
            return

        print(f"[+] Starting continuous IP rotation every {interval} seconds")
        print(f"[+] Initial IP: {get_ip()}")
        print("[+] Press Ctrl+C to stop\n")

        while True:
            cycle_count += 1
            print(f"\n--- Cycle {cycle_count} ---")
            
            if renew_identity(controller):
                new_ip = get_ip()
                print(f"[+] New IP: {new_ip}")
            else:
                print("[-] Failed to renew identity")
            
            print(f"[*] Waiting {interval} seconds before next change...")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n[!] Stopping IP rotation...")
    except Exception as e:
        print(f"[-] Unexpected error: {e}")
    finally:
        # Close controller connection properly
        if controller:
            controller.close()
        print("[+] Controller connection closed")

def parse_arguments():
    """Parse command line arguments using argparse"""
    parser = argparse.ArgumentParser(
        description="Tor IP Changer Script - Change your IP address using Tor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 main.py --setup                          # Install dependencies and configure Tor
  sudo python3 main.py --setup --single                 # Setup and change IP once
  sudo python3 main.py --setup --continuous             # Setup and change IP every 10 seconds
  sudo python3 main.py --setup --continuous -i 5       # Setup and change IP every 5 seconds
  sudo python3 main.py --continuous -i 30               # Change IP every 30 seconds (no setup)
        """
    )
    
    
    parser.add_argument(
        "--setup", "--break",
        action="store_true",
        help="Install dependencies and configure Tor"
    )
    
    # mode arguments (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--single",
        action="store_true",
        help="Change IP once and exit (default behavior)"
    )
    mode_group.add_argument(
        "--continuous", "--loop",
        action="store_true",
        help="Continuously change IP at specified intervals"
    )
    
    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=10,
        metavar="SECONDS",
        help="Interval between IP changes in continuous mode (default: 10 seconds)"
    )
    
    parser.add_argument(
        "--check-ip",
        action="store_true",
        help="Only check current IP address without changing it"
    )
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    print("Tor IP Changer Script")
    print("=" * 40)
    
    # setup if requested
    if args.setup:
        install_dependencies()
        configure_tor()
        print()

    # IP check only
    if args.check_ip:
        print(f"[+] Current IP: {get_ip()}")
        return
    
    if args.continuous:
        # validate interval
        if args.interval < 1:
            print("[-] Error: Interval must be at least 1 second")
            return
            
        print(f"[*] Continuous mode selected with {args.interval} second intervals")
        continuous_ip_change(args.interval)
        
    else:
        # Single IP change (default behavior)
        print("[*] Single IP change mode")
        controller = None
        try:
            controller = connect_to_tor()
            if not controller:
                print("[!] Tor controller unavailable. Exiting.")
                print("[!] Try running with --setup flag to configure Tor first.")
                return

            print(f"[+] Current IP: {get_ip()}")
            if renew_identity(controller):
                print(f"[+] New IP: {get_ip()}")
            else:
                print("[-] Failed to change IP")
        except Exception as e:
            print(f"[-] Error: {e}")
        finally:
            if controller:
                controller.close()

if __name__ == "__main__":
    main()