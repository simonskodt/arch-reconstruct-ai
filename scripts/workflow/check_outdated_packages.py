"""A script that checks if critical packages are up to date"""
#!/usr/bin/env python3
import json
import subprocess
import argparse

parser = argparse.ArgumentParser(description="Check that critical packages are up to date. "
"Pass package names as positional arguments (space-separated) or a single comma-separated string."
)
parser.add_argument("critical", nargs="*", help="Critical packages to check")
args = parser.parse_args()

if args.critical:
    # support both space-separated args and a single comma-separated string
    if len(args.critical) == 1 and "," in args.critical[0]:
        critical = [p.strip().lower() for p in args.critical[0].split(",") if p.strip()]
    else:
        critical = [p.strip().lower() for p in args.critical if p.strip()]
else:
    critical = ["langgraph", "langchain"]

result = subprocess.run(
    ["uv", "pip", "list", "--outdated", "--format=json"],
    capture_output=True,
    text=True,
    check=True,
)
outdated = {pkg["name"].lower(): pkg for pkg in json.loads(result.stdout)}

stale = [outdated[name] for name in critical if name in outdated]

if stale:
    print("Stale packages found:")
    for pkg in stale:
        stale_package: str = (
            f"\n{pkg['name']} "
            f"current={pkg['version']} "
            f"latest={pkg['latest_version']}"
        )
        print(stale_package)

        # Emit a GitHub Actions warning
        # (shows up in logs and PR annotations if run inside Actions)
        print(f"::warning::Critical package out of date: {stale_package}")
else:
    print("All critical packages are up to date.")
    print("::notice::All critical packages are up to date.")
