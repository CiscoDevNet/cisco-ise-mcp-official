#!/usr/bin/env python3
"""Helper script to run the ise-mcp-server unit tests with optional coverage."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
import platform


def _preferred_python(project_root: Path) -> Path:
    """Return the python executable we should use for pytest."""

    candidate = project_root / ".venv" / "bin" / "python"

    return candidate if candidate.exists() else Path(sys.executable)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ise-mcp-server test suite")
    parser.add_argument(
        "--with-coverage",
        action="store_true",
        help="Run pytest with coverage reporting for server.py",
    )
    parser.add_argument(
        "--build-container",
        action="store_true",
        help="Build the ise-mcp-server container image with Podman instead of running tests",
    )
    parser.add_argument(
        "--image-tag",
        default="ise-mcp-server:latest",
        help="Tag to apply to the built container image",
    )
    parser.add_argument(
        "--dockerfile",
        default=None,
        help="Optional path to a Dockerfile relative to the project root",
    )
    return parser.parse_args(argv)


def run_tests(with_coverage: bool) -> int:
    project_root = Path(__file__).resolve().parent
    server_dir = project_root 

    python_exe = _preferred_python(project_root)

    cmd = [str(python_exe), "-m", "pytest"]
    if with_coverage:
        # Include coverage flags when requested.
        cmd += ["--cov=./", "--cov-report=xml"]
    cmd.append("tests/")

    result = subprocess.run(cmd, cwd=server_dir)
    return result.returncode


def build_container(image_tag: str, dockerfile: str | None) -> int:
    project_root = Path(__file__).resolve().parent
    server_dir = project_root 
    print(str(server_dir))
    server_dir = project_root 
    generate_cmd = ["uv", "--directory", ".", "run", "sh", "scripts/generate_api_clients.sh"]  
    generate_result = subprocess.run(generate_cmd, cwd=server_dir)
    if generate_result.returncode != 0:
        return generate_result.returncode
    compose_cmd = ["podman", "compose", "build"]
    result = subprocess.run(compose_cmd, cwd=project_root)
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.build_container:
        return build_container(args.image_tag, args.dockerfile)

    return run_tests(args.with_coverage)


if __name__ == "__main__":
    sys.exit(main())
