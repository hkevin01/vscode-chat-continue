#!/usr/bin/env python3
"""
Kill all running automation processes.
Use this if automation gets stuck or you need to clean up before starting.
"""

import sys

import psutil


def kill_automation_processes():
    """Kill all automation-related processes."""
    print("🧹 Killing all automation processes...")

    # List of process patterns to kill
    patterns = [
        "lightweight_automation.py",
        "main_window.py",
        "run.sh",
        "continuous_automation.py",
        "vscode-chat-continue",
    ]

    killed_count = 0
    current_pid = psutil.Process().pid

    # Find and kill matching processes
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            proc_info = proc.info
            cmdline = proc_info.get("cmdline", [])

            if cmdline:
                cmdline_str = " ".join(str(arg) for arg in cmdline if arg)

                # Skip our own process
                if proc.pid == current_pid:
                    continue

                # Check if this is an automation process
                for pattern in patterns:
                    if pattern in cmdline_str:
                        try:
                            proc.terminate()
                            proc.wait(timeout=3)
                            killed_count += 1
                            print(f"   ✓ Terminated process {proc.pid}: " f"{pattern}")
                            break
                        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                            try:
                                proc.kill()
                                killed_count += 1
                                print(f"   ⚡ Force killed process " f"{proc.pid}: {pattern}")
                            except psutil.NoSuchProcess:
                                pass

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if killed_count > 0:
        print(f"✅ Killed {killed_count} automation process(es)")
    else:
        print("✅ No automation processes were running")

    return killed_count


if __name__ == "__main__":
    try:
        killed = kill_automation_processes()
        sys.exit(0 if killed >= 0 else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
