"""automation for doit-watch"""
import hashlib
from pathlib import Path
import re

import doit.tools

py_init = Path("src/doit_watch/__init__.py")
py_src = [*Path("src").rglob("*.py")]
py_setup = ["pyproject.toml"]
py_extra = ["MANIFEST.in", "LICENSE", "README.md"]
py_tests = [*Path("tests").rglob("*.py")]
py_lint = [*py_tests, *py_src, "dodo.py"]

frozen = "build/pip-freeze.txt"
sha_sums = "dist/SHA256SUMS"

version = re.findall(
    """__version__ = \"(.*)\"""",
    py_init.read_text(encoding="utf-8"),
)[0]
py_dist = {
    "sdist": f"dist/doit-watch-{version}.tar.gz",
    "wheel": f"dist/doit_watch-{version}-py3-none-any.whl",
}


def task_setup():
    """Performs a development install."""

    yield dict(
        name="pip",
        file_dep=py_setup,
        targets=[frozen],
        actions=[
            (doit.tools.create_folder, ["build"]),
            "flit install --pth-file",
            "python -m pip check",
            "python -m pip freeze > build/pip-freeze.txt",
        ],
    )


def task_fix():
    """Ensures code style."""

    yield dict(
        name="black",
        file_dep=[*py_setup, *py_lint],
        actions=[
            ["black", *py_lint],
        ],
    )


def task_check():
    """Check code style."""

    yield dict(
        name="pyflakes",
        file_dep=[*py_setup, *py_lint],
        actions=[["pyflakes", *py_lint]],
    )

    yield dict(
        name="black",
        file_dep=[*py_setup, *py_lint],
        actions=[["black", "--check", *py_lint]],
    )

    for suite, files in {"tests": py_tests, "src": py_src}.items():
        mypy_dir = f"build/reports/mypy/{suite}"
        yield dict(
            name=f"mypy:{suite}",
            file_dep=[*py_setup, *py_lint, *py_tests],
            actions=[["mypy", f"--html-report={mypy_dir}", *files]],
            targets=[f"{mypy_dir}/index.html"],
        )


def task_test():
    """Run tests."""

    html_cov = "build/reports/htmlcov"
    yield dict(
        name="cov",
        file_dep=[*py_src, *py_setup, *py_tests, frozen],
        targets=[".coverage", f"{html_cov}/index.html"],
        actions=[
            "pytest tests -vv --cov=doit_watch"
            " --cov-report=term-missing:skip-covered"
            f" --cov-report=html:{html_cov}"
            " --no-cov-on-fail"
        ],
    )


def task_build():
    """Build distributions."""

    for dist_format, dist in py_dist.items():
        yield dict(
            name=dist_format,
            file_dep=[*py_src, *py_setup, *py_extra],
            targets=[dist],
            actions=[f"flit build --setup-py --format={dist_format}"],
        )

    yield dict(
        name="hash",
        file_dep=[*py_dist.values()],
        targets=[sha_sums],
        actions=[
            (hash_files, [sha_sums, *py_dist.values()]),
            lambda: print(Path(sha_sums).read_text()),
        ],
    )


def hash_files(hash_file, *hash_deps):
    """Emulate the output of sha256sums (even on windows)."""
    lines = [
        "{}  {}".format(hashlib.sha256(d.read_bytes()).hexdigest(), d.name)
        for d in sorted(map(Path, hash_deps))
    ]
    Path(hash_file).write_text("\n".join(lines))
