
import subprocess
import sys
import os
import shutil


print(os.environ["PATH"])

print("Running solver_staticCgen.py to produce board variables")

import solver_StaticC_gen

print("solver_StaticC_gen.py completed")

C_FILE = "solve_v1.c"
EXE_FILE = "solver.exe"

# locate gcc: prefer env var, then shutil.which, then try bash -lc which
gcc_path = os.environ.get("GCC") or os.environ.get("CC") or shutil.which("gcc") or shutil.which("gcc.exe")

use_bash = False
bash_compile_cmd = None

if not gcc_path:
    # try bash if available (e.g. MSYS2 / Git Bash)
    bash = shutil.which("bash") or shutil.which("bash.exe")
    if bash:
        # ask bash where gcc is
        try:
            p = subprocess.run([bash, "-lc", "which gcc"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            out = p.stdout.strip()
            if out:
                # we'll use bash to run the full compile command
                use_bash = True
                bash_compile_cmd = f"gcc -O3 {C_FILE} -o {EXE_FILE}"
                print("gcc found inside bash, will run compile via bash:", out)
            else:
                print("bash found but gcc not found inside bash.")
        except Exception as e:
            print("Error checking bash for gcc:", e)
    else:
        print("gcc not found and bash not present.")

else:
    print("Using gcc at:", gcc_path)

# 1) Compile
print("Compiling...")
if use_bash:
    result = subprocess.run(
        [bash, "-lc", bash_compile_cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
elif gcc_path:
    compile_cmd = [
        gcc_path,
        "-O3",
        C_FILE,
        "-o",
        EXE_FILE
    ]
    print("Compile command:", compile_cmd)
    result = subprocess.run(
        compile_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
else:
    print("ERROR: gcc not found and bash not available.")
    sys.exit(1)

if result.returncode != 0:
    print("Compilation failed!")
    print(result.stderr)
    sys.exit(1)

print("Compilation successful.")

# 2) Run
print("\nRunning solver...\n")
run = subprocess.run(
    [f".\\{EXE_FILE}"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

print(run.stdout)

if run.stderr:
    print("Errors:", run.stderr)
 