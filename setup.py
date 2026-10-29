#!/usr/bin/env python3
import os
import sys
import json


def find_ghidra():
    """Bilgisayardaki yaygın Ghidra kurulum yerlerini otomatik tarar."""
    print("🔍 Scanning system for Ghidra installation...")
    common_paths = []

    if sys.platform == "win32":
        common_paths = [r"C:\ghidra", r"C:\Tools\ghidra", r"D:\ghidra"]
    elif sys.platform == "darwin":
        common_paths = ["/Applications/ghidra", "/usr/local/share/ghidra"]
    else:
        common_paths = [
            "/opt/ghidra",
            "/usr/share/ghidra",
            os.path.expanduser("~/ghidra"),
        ]

    for path in common_paths:
        if os.path.exists(os.path.join(path, "support", "analyzeHeadless")):
            return path

    # Bulamazsa kullanıcıya sorar
    print("⚠️  Ghidra could not be found automatically.")
    user_path = input("📂 Please paste your absolute Ghidra folder path: ").strip()
    return user_path


def update_ide_configs(ghidra_path):
    """Claude Desktop ve Cursor gibi IDE konfigürasyonlarını otomatik günceller."""
    home = os.path.expanduser("~")
    main_script_path = os.path.abspath("main.py")

    # Hedef config yolları listesi (Claude Desktop, Cursor vb.)
    config_targets = []

    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        config_targets.append(
            os.path.join(appdata, "Claude", "claude_desktop_config.json")
        )
        config_targets.append(
            os.path.join(appdata, "Cursor", "User", "globalStorage", "mcpServers.json")
        )
    elif sys.platform == "darwin":
        config_targets.append(
            os.path.join(
                home,
                "Library",
                "Application Support",
                "Claude",
                "claude_desktop_config.json",
            )
        )
        config_targets.append(
            os.path.join(
                home,
                "Library",
                "Application Support",
                "Cursor",
                "User",
                "globalStorage",
                "mcpServers.json",
            )
        )
    else:
        config_targets.append(
            os.path.join(home, ".config", "Claude", "claude_desktop_config.json")
        )
        config_targets.append(
            os.path.join(
                home, ".config", "Cursor", "User", "globalStorage", "mcpServers.json"
            )
        )

    for config_path in config_targets:
        if not os.path.exists(os.path.dirname(config_path)):
            continue

        print(f"⚙️  Configuring: {config_path}")
        config_data = {"mcpServers": {}}

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except:
                pass

        config_data["mcpServers"] = config_data.get("mcpServers", {})
        config_data["mcpServers"]["fastrea"] = {
            "command": sys.executable,
            "args": [main_script_path],
            "env": {"GHIDRA_PATH": ghidra_path},
        }

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

    print("\n✅ FastREA successfully linked into your IDEs and Claude Desktop!")


if __name__ == "__main__":
    print("⚡ FastREA Environment Provisioner Started...")
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
