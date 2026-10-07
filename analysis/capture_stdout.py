"""Run an analysis script and keep its stdout as a paper/generated markdown file.

`make tables` must not leave a headline number only on a terminal. For the
scripts whose report is a printed scorecard rather than a table, this wrapper
runs the script unchanged, echoes its stdout live, and on success writes the
stdout VERBATIM (fenced) under a header naming the script and git sha. Nothing
is reformatted, so every figure is exactly what the script printed. A failing
script writes no file and its exit status is returned.

Usage: python analysis/capture_stdout.py OUT_NAME TITLE SCRIPT [ARGS...]
"""

from __future__ import annotations

import subprocess
import sys

from analysis import paper_md


def run_and_capture(out_name: str, title: str, script: str, args: list[str], out_dir=paper_md.OUT_DIR) -> int:
    """Run `script`, echo and capture its stdout, write the markdown on success.

    Args:
        out_name: File name under `out_dir`.
        title: Document title.
        script: Script path, run with this interpreter.
        args: Extra arguments for the script.
        out_dir: Output directory.

    Returns:
        The script's exit status.
    """
    proc = subprocess.Popen([sys.executable, script, *args], stdout=subprocess.PIPE, text=True)
    captured: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        sys.stdout.write(line)
        captured.append(line)
    rc = proc.wait()
    if rc != 0:
        return rc
    cmd = " ".join([script, *args])
    text = paper_md.header(title, script, f"Verbatim stdout of `{cmd}`.")
    text += "\n```text\n" + "".join(captured).rstrip("\n") + "\n```\n"
    paper_md.write(out_name, text, out_dir)
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 4:
        print(__doc__)
        return 2
    return run_and_capture(argv[1], argv[2], argv[3], argv[4:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
