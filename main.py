#!/usr/bin/env python3
import os
import sys
import json
import subprocess


def create_ghidra_script(target_dir):
    """Ghidra'nın arka planda C çıktısı vermesi için gereken Java kodunu canlı üretir."""
    java_code = """
    import java.io.File;
    import java.util.ArrayList;
    import ghidra.app.script.GhidraScript;
    import ghidra.app.util.exporter.CppExporter;
    public class FastREADecompile extends GhidraScript {
        @Override
        public void run() throws Exception {
            String[] args = getScriptArgs();
            File outputFile = new File(args[0]);
            CppExporter exporter = new CppExporter();
            exporter.export(outputFile, currentProgram, null, monitor);
        }
    }
    """
    script_path = os.path.join(target_dir, "FastREADecompile.java")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(java_code.strip())
    return script_path


def run_mcp_server():
    """Claude/Cursor ile konuşan ultra hafif MCP Protokol sunucusu."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "mcp"], stdout=subprocess.DEVNULL
        )
        from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("FastREA")

    @mcp.tool()
    def fastrea_analyze(file_path: str) -> str:
        """Decompiles a native binary (EXE/ELF) via headless Ghidra and returns pure C code."""
        if not os.path.exists(file_path):
            return f"Error: Target file not found at {file_path}"

        abs_path = os.path.abspath(file_path)
        directory = os.path.dirname(abs_path)
        filename = os.path.basename(abs_path)
        output_c = os.path.join(directory, f"{filename}_decompiled.c")
        temp_proj = os.path.join(directory, "fastrea_temp_proj")

        ghidra_path = os.environ.get("GHIDRA_PATH", "")
        ghidra_headless = os.path.join(ghidra_path, "support", "analyzeHeadless")

        # Java otomasyon dosyasını aynı klasörde dinamik oluştur
        script_file = create_ghidra_script(directory)

        # Headless Ghidra Komut Dizisi
        cmd = [
            ghidra_headless,
            temp_proj,
            "FastREA_Proj",
            "-import",
            abs_path,
            "-scriptPath",
            directory,
            "-postScript",
            "FastREADecompile.java",
            output_c,
            "-deleteProject",
        ]

        try:
            subprocess.run(
                cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            # Geçici oluşturduğumuz java scriptini temizle
            if os.path.exists(script_file):
                os.remove(script_file)

            if os.path.exists(output_c):
                with open(output_c, "r", encoding="utf-8") as f:
                    c_code = f.read()
                return f"Success! C source saved to: '{output_c}'\n\n=== SOURCE CODE ===\n\n{c_code}"

            return "Error: Ghidra executed but failed to generate the C source file."
        except Exception as e:
            return f"Ghidra execution failed: {str(e)}"

    mcp.run()


if __name__ == "__main__":
    run_mcp_server()
