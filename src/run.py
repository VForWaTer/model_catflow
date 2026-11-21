import os
import shutil
import subprocess
import sys
from pathlib import Path

from parameters import get_data, get_logger, get_parameters

params = get_parameters()
data = get_data()
logger = get_logger()

toolname = os.environ.get("TOOL_RUN", "catflow").lower()

logger.info("start", "Starting tool run", tool=toolname)
logger.info(
    "input-loaded",
    "Loaded validated parameters and data paths",
    tool=toolname,
    parameter_count=len(vars(params)),
    data_keys=sorted(data.keys()),
)

if toolname == "catflow":
    # ------------------------------------------------------------------
    # Mount layout (root of the container):
    #   /in    - input volume (contains catflow.in, run_cat.in, + inputs)
    #   /out   - output volume (CATFLOW writes results here)
    #   /src   - tool code (run.py, tool.yml) + catflow source
    # Binary is pre-built at /usr/local/bin/catflow.exe.
    #
    # CATFLOW expects the exe, in/, out/ and control files in the SAME
    # parent directory and writes directly to out/. We use the container
    # root ("/" - which is the parent of /in and /out) as that directory.
    # ------------------------------------------------------------------
    parent_dir = Path("/")          # parent of /in and /out

    # 1) Copy catflow.exe into the parent directory
    exe_src = Path("/usr/local/bin/catflow.exe")
    exe_dst = parent_dir / "catflow.exe"
    shutil.copy2(exe_src, exe_dst)
    exe_dst.chmod(0o755)
    logger.info("copied-exe", "Copied catflow.exe to parent directory",
                src=str(exe_src), dst=str(exe_dst))

    # 2) Copy control files from in/ up to the parent directory
    in_dir = Path(data["inp_dir"])
    control_files = ["run_cat.in", "catflow.in"]
    for fname in control_files:
        src = in_dir / fname
        if src.exists():
            shutil.copy2(src, parent_dir / fname)
            logger.info("copied-control", "Copied control file to parent dir",
                        file=fname)
        else:
            logger.warning("missing-control", "Control file not found in /in",
                           file=fname)
            raise FileNotFoundError(
                f"Required control file not found in /in: {fname}"
            )

    # 3) Run CATFLOW from the parent directory (cwd=/).
    #    out/ (/out) is a sibling, so CATFLOW writes results directly to it.
    logger.info("running-catflow", "Launching compiled CATFLOW binary",
                tool=toolname, cwd=str(parent_dir))
    result = subprocess.run(
        ["catflow.exe"],
        cwd=str(parent_dir),
        capture_output=True,
        text=True,
    )

    logger.info("catflow-finished", "CATFLOW process completed",
                tool=toolname, returncode=result.returncode,
                stdout_tail=result.stdout[-2000:],
                stderr_tail=result.stderr[-2000:])

    if result.returncode != 0:
        logger.error("catflow-error", "CATFLOW exited with non-zero status",
                     tool=toolname, returncode=result.returncode,
                     stderr=result.stderr[-4000:])
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        sys.exit(result.returncode)

    if os.environ.get("CATFLOW_VERBOSE", "0") == "1":
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)

    logger.info("finished", "CATFLOW run finished successfully", tool=toolname)
else:
    logger.error("error", "Requested tool is not implemented", tool=toolname)
    raise AttributeError(
        f"Either no TOOL_RUN environment variable available, or '{toolname}' is not valid.\n"
    ) 
