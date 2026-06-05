import os
import re
import subprocess
import sys
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init(autoreset=True)

BANNER = r"""
░█▀▀▄░█░▒█░▀█▀░▄▀▀▄░░░▀▀█▀▀░█▀▀▄░█▀▄▀█░▄▀▀▄░█▀▀░█▀▀▄
▒█▄▄█░█░▒█░░█░░█░░█░░░░▒█░░░█▄▄█░█░▀░█░█▄▄█░█▀▀░█▄▄▀
▒█░▒█░░▀▀▀░░▀░░░▀▀░░░░░▒█░░░▀░░▀░▀░░▒▀░█░░░░▀▀▀░▀░▀▀
"""

DESCRIPTION = """
AutoTamper is an automatic tamper test tool using SQLMap.
It runs SQLMap with various tamper scripts to identify which
tamper script works best with your target URL.
"""


def print_banner() -> None:
    """Print the centered ASCII banner and description."""
    lines = BANNER.strip().split("\n")
    width = max(len(line) for line in lines)
    print("\n\n")
    for line in lines:
        print(Fore.CYAN + line.center(width))
    print(Fore.WHITE + DESCRIPTION.center(width))
    print("\n")


def get_user_inputs() -> tuple[str, str, list[str]]:
    """Prompt the user for URL, SQLMap options, and optional static tampers."""
    url = input(
        f"{Fore.YELLOW}Enter the URL with injection point "
        f"(e.g., https://example.com/index.php?id=1*): {Style.RESET_ALL}"
    ).strip()

    command_opts = input(
        f"{Fore.YELLOW}Enter SQLMap options "
        f"(e.g., --batch --current-db --level 5 --risk 3 --dbms mysql): {Style.RESET_ALL}"
    ).strip()

    static_input = input(
        f"{Fore.YELLOW}Enter static tamper scripts to always apply "
        f"(comma-separated, or leave empty): {Style.RESET_ALL}"
    ).strip()

    static_tampers = [t.strip() for t in static_input.split(",") if t.strip()]
    return url, command_opts, static_tampers


def extract_target_host(url: str) -> str | None:
    """Extract the hostname from a URL, or return None if not found."""
    match = re.search(r"https?://([^/]+)", url)
    return match.group(1) if match else None


def run_sqlmap(base_cmd: str, output_dir: Path, tamper: str) -> None:
    """
    Run SQLMap with a specific tamper script.

    Uses subprocess instead of os.system for better safety and control.
    The tamper argument accepts either a script name or a full path.
    """
    cmd = f'{base_cmd} --output-dir="{output_dir}" --tamper "{tamper}"'
    try:
        subprocess.run(cmd, shell=True, check=False)
    except Exception as exc:
        print(f"{Fore.RED}[!] Error running sqlmap: {exc}{Style.RESET_ALL}")


def log_has_successful_injection(log_path: Path) -> bool:
    """
    Return True if the SQLMap log file indicates a successful injection.

    Looks for all three key lines anywhere in the log (order-independent),
    which fixes the original bug where nested line-by-line reading never
    matched all three conditions simultaneously.
    """
    if not log_path.exists():
        return False

    try:
        content = log_path.read_text(errors="replace").lower()
    except OSError:
        return False

    return (
        "web server operating system" in content
        and "web application technology" in content
        and "available databases" in content
    )


def find_working_tamper(
    base_cmd: str,
    tamper_dir: Path,
    output_dir: Path,
    target_host: str,
    static_tampers: list[str],
) -> str | None:
    """
    Iterate over all tamper scripts and return the first one that
    produces a successful injection log, or None if none works.
    """
    log_path = output_dir / target_host / "log"

    # Run with static tampers first (combined, as SQLMap supports comma-separated)
    if static_tampers:
        combined = ",".join(static_tampers)
        print(f"{Fore.CYAN}[*] Trying static tampers: {combined}{Style.RESET_ALL}")
        run_sqlmap(base_cmd, output_dir, combined)
        if log_has_successful_injection(log_path):
            return combined

    # Discover all tamper scripts in the tamper directory
    try:
        entries = sorted(
            entry.name
            for entry in tamper_dir.iterdir()
            if entry.suffix == ".py" and entry.name != "__init__.py"
        )
    except FileNotFoundError:
        print(f"{Fore.RED}[!] Tamper directory not found: {tamper_dir}{Style.RESET_ALL}")
        return None

    total = len(entries)
    for idx, entry in enumerate(entries, start=1):
        tamper_path = tamper_dir / entry
        print(
            f"{Fore.CYAN}[{idx}/{total}] Testing tamper: {entry}{Style.RESET_ALL}"
        )
        run_sqlmap(base_cmd, output_dir, str(tamper_path))

        if log_has_successful_injection(log_path):
            return entry

    return None


def main() -> None:
    print_banner()

    url, command_opts, static_tampers = get_user_inputs()

    target_host = extract_target_host(url)
    if not target_host:
        print(f"{Fore.RED}[!] Invalid URL format. Please include http:// or https://.{Style.RESET_ALL}")
        sys.exit(1)

    base_dir = Path.cwd()
    tamper_dir = base_dir / "tamper"
    output_dir = base_dir / "output"

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Detect sqlmap entry point (sqlmap.py or sqlmap)
    sqlmap_cmd = "sqlmap.py" if (base_dir / "sqlmap.py").exists() else "sqlmap"
    base_cmd = f'{sqlmap_cmd} -u "{url}" {command_opts}'

    print(f"\n{Fore.GREEN}[*] Target   : {url}")
    print(f"[*] Command  : {base_cmd}")
    print(f"[*] Tampers  : {tamper_dir}")
    print(f"[*] Output   : {output_dir}{Style.RESET_ALL}\n")

    working_tamper = find_working_tamper(
        base_cmd, tamper_dir, output_dir, target_host, static_tampers
    )

    if working_tamper:
        print(f"\n{Fore.GREEN}[+] Working tamper found: {working_tamper}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}[-] No working tamper found for this target.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
