# FastREA ⚡

FastREA is an ultra-lightweight, zero-overhead Model Context Protocol (MCP) server for binary decompilation. Inspired by the core concepts of `morluto/rea`, it eliminates heavy multi-agent loops and complex dependencies. Instead, it provides your LLM with a single, laser-focused capability: **Convert native binaries into clean C source code instantly using headless Ghidra.**

---

## 🛠️ Architecture Overview

The system consists of only two files:
1. `setup.py`: A one-time initialization script that automatically scans your environment, detects Ghidra, and registers FastREA across your IDEs and Claude Desktop config files.
2. `main.py`: The lightweight stateless MCP engine called by the model to orchestrate headless Ghidra execution and stream pure C output directly into the model context.

---

## 📦 Dependencies & Installation

FastREA relies on minimal external components. Ensure you have Python 3.10+ and [Ghidra](https://ghidra-sre.org) installed locally.

### Required Python Libraries
To run the MCP engine, you must install the official Model Context Protocol Python SDK. Run the following command in your terminal:

```bash
pip install mcp
```

---

## 🚀 Quick Start

### 1. Provision Environment
Run the automated configuration script. It will automatically scan common paths for Ghidra and inject the FastREA integration directly into Claude Desktop and Cursor configurations:

```bash
python setup.py
```

### 2. Execution & Usage
Restart your Claude Desktop application or Cursor IDE. You can now prompt your model naturally to handle binary reversing workflows:

> *"Use fastrea to analyze the binary at `/absolute/path/to/target.exe` and explain its primary protection routines."*

### 🔄 Under the Hood Process:
1. The model detects your instruction and triggers the `fastrea_analyze` MCP tool inside `main.py`.
2. `main.py` dynamically writes a clean Java decompile script and boots Ghidra in headless mode.
3. Ghidra exports a flat `target.exe_decompiled.c` source file directly in the executable's directory.
4. FastREA reads the file contents and provides the structured code back to the LLM.
5. The model parses the pristine raw C source code flawlessly without any context bloat.

---

## 📄 License
This project is open-source and licensed under the [MIT License](LICENSE).
