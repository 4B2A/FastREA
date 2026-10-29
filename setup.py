#!/usr/bin/env python3
import os
import sys
import json
import glob
import subprocess


def install_dependencies():
  
    print("📦 Installing required Python packages...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "mcp"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("✅ Python dependencies installed successfully.")
    except Exception as e:
        print(f"⚠️  Failed to install dependencies automatically: {e}")


def find_ghidra():
   
    print("🔍 Scanning system for Ghidra installation...")
    search_patterns = []

    if sys.platform == "win32":
        search_patterns = [
            r"C:\ghidra*",
            r"C:\Tools\ghidra*",
            r"D:\ghidra*",
            r"C:\Program Files\ghidra*",
        ]
    elif sys.platform == "darwin":
        search_patterns = [
            "/Applications/ghidra*",
            "/usr/local/share/ghidra*",
            os.path.expanduser("~/ghidra*"),
        ]
    else:
        search_patterns = [
            "/opt/ghidra*",
            "/usr/share/ghidra*",
            os.path.expanduser("~/ghidra*"),
        ]

    
    for pattern in search_patterns:
        for path in glob.glob(pattern):
            if os.path.exists(os.path.join(path, "support", "analyzeHeadless")):
                return os.path.abspath(path)

    print("⚠️  Ghidra could not be found automatically.")
    user_path = input("📂 Please paste your absolute Ghidra folder path: ").strip()
    return os.path.abspath(user_path)


def update_ide_configs(ghidra_path):
    
    home = os.path.expanduser("~")
   
    main_script_path = os.path.abspath("main.py").replace("\\", "/")
    python_exe = sys.executable.replace("\\", "/")

    
    config_targets = []

    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        config_targets.append(
            (
                "claude",
                os.path.join(appdata, "Claude", "claude_desktop_config.json"),
            )
        )
        config_targets.append(
            (
                "cursor",
                os.path.join(
                    appdata,
                    "Cursor",
                    "User",
                    "globalStorage",
                    "mcpServers.json",
                ),
            )
        )
    elif sys.platform == "darwin":
        config_targets.append(
            (
                "claude",
                os.path.join(
                    home,
                    "Library",
                    "Application Support",
                    "Claude",
                    "claude_desktop_config.json",
                ),
            )
        )
        config_targets.append(
            (
                "cursor",
                os.path.join(
                    home,
                    "Library",
                    "Application Support",
                    "Cursor",
                    "User",
                    "globalStorage",
                    "mcpServers.json",
                ),
            )
        )
    else:
        config_targets.append(
            (
                "claude",
                os.path.join(
                    home, ".config", "Claude", "claude_desktop_config.json"
                ),
            )
        )
        config_targets.append(
            (
                "cursor",
                os.path.join(
                    home,
                    ".config",
                    "Cursor",
                    "User",
                    "globalStorage",
                    "mcpServers.json",
                ),
            )
        )

    server_config = {
        "command": python_exe,
        "args": [main_script_path],
        "env": {"GHIDRA_PATH": ghidra_path.replace("\\", "/")},
    }

    for config_type, config_path in config_targets:
        if not os.path.exists(os.path.dirname(config_path)):
            continue

        print(f"⚙️  Configuring {config_type.upper()}: {config_path}")
        config_data = {}

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except:
                pass

        if config_type == "claude":
            config_data["mcpServers"] = config_data.get("mcpServers", {})
            config_data["mcpServers"]["fastrea"] = server_config
        elif config_type == "cursor":
           
            if "mcpServers" in config_data:
                config_data["mcpServers"]["fastrea"] = server_config
            else:
                config_data["fastrea"] = server_config

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

    print("\n✅ FastREA successfully linked into your IDEs!")


if __name__ == "__main__":
    print("⚡ FastREA Environment Provisioner Started...")
    install_dependencies()
    ghidra_dir = find_ghidra()

    if not ghidra_dir or not os.path.exists(
        os.path.join(ghidra_dir, "support", "analyzeHeadless")
    ):
        print("❌ Invalid Ghidra path! Aborting setup.")
        sys.exit(1)

    print(f"🎯 Ghidra Found At: {ghidra_dir}")
    update_ide_configs(ghidra_dir)
    print("\n🚀 Setup Complete. Restart your Claude Desktop or Cursor and type:")
    print("👉 'Analyze this binary using fastrea: /path/to/binary.exe'")
