# Tor IP Changer Script

## Overview

The Tor IP Changer Script is a Python utility designed to automate the process of changing your IP address through the Tor network. It provides both single-use and continuous IP rotation capabilities, making it useful for privacy-conscious users, researchers, and developers who need to regularly change their network identity.

## Demo Video

📹 [View Demo Video](https://youtu.be/D3N57GtJG5c)

## Features

- **Automatic Dependency Installation**: Installs required packages including Tor and Python dependencies
- **Tor Configuration Management**: Automatically configures Tor with proper control port settings
- **IP Address Verification**: Checks and displays your current external IP address
- **Single IP Change**: Change your Tor exit node once and exit
- **Continuous IP Rotation**: Continuously change IP addresses at customizable intervals
- **Graceful Shutdown**: Properly handles controller connections and cleanup

## Requirements

- Linux operating system (tested on Kali Linux, Ubuntu, Debian)
- Python 3.x
- sudo privileges for package installation and Tor configuration

## Installation

1. Clone or download the script to your local machine

```bash
git clone https://github.com/Raunaksplanet/Tor-IP-Changer-Script.git
```

2. Go to the directory
```bash
cd Tor-IP-Changer-Script
```

3. Install the dependencies

```bash
pip install -r requirements.txt
```

4. Make the script executable if desired: 
```bash
chmod +x torIPChangerScript.py
```


## Usage

### First-Time Setup (Install Dependencies)
```bash
sudo python3 torIPChangerScript.py --break
```

### Continuous IP Rotation (Every 10 seconds)
```bash
sudo python3 torIPChangerScript.py --break --continuous
```

### Custom Interval Rotation (Every 5 seconds example)
```bash
sudo python3 torIPChangerScript.py --break --continuous --interval 5
```

### Single IP Change
```bash
sudo python3 torIPChangerScript.py --break
```

## How It Works

1. **Dependency Installation**: The script installs Tor, Python pip, and required Python packages (stem, requests with SOCKS support)
2. **Tor Configuration**: Configures Tor to run with:
   - SOCKS proxy on port 9050
   - Control port on 9051
   - Disabled cookie authentication for controller access
3. **Controller Connection**: Establishes a connection to the Tor control port
4. **IP Rotation**: Sends NEWNYM signals to Tor to request new circuits
5. **IP Verification**: Uses httpbin.org to verify IP address changes

## Command Line Arguments

- `--break`: Install dependencies and configure Tor (required for first run)
- `--continuous` or `--loop`: Enable continuous IP rotation
- `--interval [seconds]`: Set custom interval for IP changes (default: 10 seconds)

## File Structure

- `torIPChangerScript.py`: Main script file
- `/etc/tor/torrc`: Tor configuration file (automatically modified by the script)

## Important Notes

- The script requires root privileges to install packages and modify Tor configuration
- Continuous mode runs until manually stopped with Ctrl+C
- The script includes proper error handling and cleanup procedures
- IP changes may take a few seconds to propagate through the Tor network

## Troubleshooting

1. **Port Already in Use**: If ports 9050 or 9051 are already occupied, the script will detect this and skip Tor restart
2. **Controller Connection Issues**: Ensure Tor is running and properly configured
3. **IP Verification Failures**: Check internet connectivity and Tor network status

## Security Considerations

- This script modifies system-wide Tor configuration
- Use with caution on production systems
- Consider the legal and ethical implications of frequent IP changes in your jurisdiction

## License

This script is provided for educational and research purposes. Users are responsible for complying with local laws and terms of service.
