
import os
import sys
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FastREA")


def create_ghidra_script(target_dir):
    
    java_code = """
    import java.io.File;
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


@mcp.tool()
def fastrea_analyze(file_path: str) -> str:

    if not os.path.exists(file_path):
        return f"Error: Target file not found at local path: {file_path}"

    abs_path = os.path.abspath(file_path)
    directory = os.path.dirname(abs_path)
    filename = os.path.basename(abs_path)

    output_c = os.path.join(directory, f"{filename}_decompiled.c")
   
    temp_proj = os.path.join(directory, f"fastrea_tmp_{filename}")

    ghidra_path = os.environ.get("GHIDRA_PATH", "")
    if not ghidra_path:
        return "Error: GHIDRA_PATH environment variable is not set. Please rerun setup.py."

    ghidra_headless = os.path.join(ghidra_path, "support", "analyzeHeadless")
    if sys.platform == "win32" and not ghidra_headless.endswith(".bat"):
        ghidra_headless += ".bat"

    if not os.path.exists(ghidra_headless):
        return f"Error: Headless Ghidra analyzer not found at: {ghidra_headless}"

    script_file = create_ghidra_script(directory)

  
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
        result = subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True
        )

       
        if os.path.exists(script_file):
            os.remove(script_file)

        if result.returncode != 0:
            return f"Ghidra execution failed with exit code {result.returncode}.\nError Log:\n{result.stderr}"

        if os.path.exists(output_c):
            with open(output_c, "r", encoding="utf-8") as f:
                c_code = f.read()
            return f"Success! C source saved to: '{output_c}'\n\n=== SOURCE CODE ===\n\n{c_code}"

        return "Error: Ghidra process completed but output C file was not generated."

    except Exception as e:
        return f"Exception occurred during execution: {str(e)}"


if __name__ == "__main__":
    mcp.run()
