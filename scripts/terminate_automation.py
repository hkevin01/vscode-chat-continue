#!/usr/bin/env python3
"""
VS Code Chat Continue Automation Terminator
Safely terminates all running automation processes
"""

import argparse
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class AutomationTerminator:
    """Terminates VS Code Chat Continue automation processes."""
    
    def __init__(self, verbose: bool = False, force: bool = False):
        """Initialize the terminator.
        
        Args:
            verbose: Enable verbose output
            force: Use SIGKILL instead of SIGTERM
        """
        self.verbose = verbose
        self.force = force
        self.terminated_count = 0
        self.failed_count = 0
        
        # Setup logging
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Process patterns to search for (specific automation scripts only)
        self.automation_patterns = [
            'lightweight_automation.py',
            'continuous_automation.py',
            'safe_automation.py',
            'main_window.py',
            'automation_engine.py',
            'src/main.py',
            'scripts/main.py'
        ]
    
    def find_automation_processes(self) -> List[Tuple[int, str, str]]:
        """Find all automation-related processes.
        
        Returns:
            List of tuples (pid, name, cmdline)
        """
        processes = []
        current_pid = os.getpid()
        
        if HAS_PSUTIL:
            # Use psutil for better process detection
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    pid = proc_info['pid']
                    name = proc_info['name'] or ''
                    cmdline = proc_info['cmdline'] or []
                    
                    # Skip our own process
                    if pid == current_pid:
                        continue
                    
                    # Check if this is an automation process
                    cmdline_str = ' '.join(str(arg) for arg in cmdline if arg)
                    
                    for pattern in self.automation_patterns:
                        if pattern in cmdline_str or pattern in name:
                            processes.append((pid, name, cmdline_str))
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        else:
            # Fallback to ps command
            try:
                result = subprocess.run(
                    ['ps', 'aux'], 
                    capture_output=True, 
                    text=True
                )
                
                for line in result.stdout.split('\n')[1:]:  # Skip header
                    if not line.strip():
                        continue
                    
                    parts = line.split(None, 10)
                    if len(parts) >= 11:
                        pid = int(parts[1])
                        command = parts[10]
                        
                        # Skip our own process
                        if pid == current_pid:
                            continue
                        
                        for pattern in self.automation_patterns:
                            if pattern in command:
                                processes.append((pid, parts[10], command))
                                break
                                
            except (subprocess.SubprocessError, ValueError):
                self.logger.error("❌ Failed to get process list")
        
        return processes
    
    def terminate_process(self, pid: int, name: str, cmdline: str) -> bool:
        """Terminate a single process.
        
        Args:
            pid: Process ID
            name: Process name
            cmdline: Command line
            
        Returns:
            True if successfully terminated
        """
        try:
            if HAS_PSUTIL:
                # Use psutil for better process handling
                proc = psutil.Process(pid)
                
                if self.force:
                    proc.kill()
                    signal_name = "SIGKILL"
                else:
                    proc.terminate()
                    signal_name = "SIGTERM"
                
                # Wait for process to terminate
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    if not self.force:
                        # Force kill if graceful termination failed
                        self.logger.warning(f"⚠️  Process {pid} didn't respond to SIGTERM, using SIGKILL")
                        proc.kill()
                        proc.wait(timeout=3)
                        signal_name = "SIGKILL"
                
            else:
                # Fallback to kill command
                signal_type = signal.SIGKILL if self.force else signal.SIGTERM
                signal_name = "SIGKILL" if self.force else "SIGTERM"
                
                os.kill(pid, signal_type)
                
                # Wait a bit for process to terminate
                time.sleep(1)
                
                # Check if process still exists
                try:
                    os.kill(pid, 0)  # Check if process exists
                    if not self.force:
                        # Force kill if still running
                        os.kill(pid, signal.SIGKILL)
                        signal_name = "SIGKILL"
                        time.sleep(0.5)
                except OSError:
                    pass  # Process is gone
            
            self.logger.info(f"✅ Terminated PID {pid} ({signal_name}): {name}")
            if self.verbose:
                self.logger.debug(f"   Command: {cmdline[:100]}...")
            
            self.terminated_count += 1
            return True
            
        except (psutil.NoSuchProcess, OSError) as e:
            if "No such process" in str(e):
                self.logger.debug(f"🔍 Process {pid} already terminated")
                return True
            else:
                self.logger.error(f"❌ Failed to terminate PID {pid}: {e}")
                self.failed_count += 1
                return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error terminating PID {pid}: {e}")
            self.failed_count += 1
            return False
    
    def terminate_all(self) -> bool:
        """Terminate all automation processes.
        
        Returns:
            True if all processes were terminated successfully
        """
        self.logger.info("🔍 Searching for VS Code Chat Continue automation processes...")
        
        processes = self.find_automation_processes()
        
        if not processes:
            self.logger.info("✅ No automation processes found")
            return True
        
        self.logger.info(f"📋 Found {len(processes)} automation process(es)")
        
        if self.verbose:
            for pid, name, cmdline in processes:
                self.logger.debug(f"   PID {pid}: {name} - {cmdline[:80]}...")
        
        self.logger.info(f"🛑 Terminating processes with {'SIGKILL' if self.force else 'SIGTERM'}...")
        
        # Terminate all processes
        for pid, name, cmdline in processes:
            self.terminate_process(pid, name, cmdline)
        
        # Final check
        remaining = self.find_automation_processes()
        if remaining:
            self.logger.warning(f"⚠️  {len(remaining)} process(es) still running after termination")
            if not self.force and remaining:
                self.logger.info("💡 Use --force flag to send SIGKILL to remaining processes")
        
        # Summary
        total = len(processes)
        self.logger.info("")
        self.logger.info("📊 Termination Summary:")
        self.logger.info(f"   ✅ Successfully terminated: {self.terminated_count}")
        if self.failed_count > 0:
            self.logger.info(f"   ❌ Failed to terminate: {self.failed_count}")
        if remaining:
            self.logger.info(f"   ⚠️  Still running: {len(remaining)}")
        
        return self.failed_count == 0 and len(remaining) == 0
    
    def cleanup_temp_files(self):
        """Clean up temporary files created by automation."""
        self.logger.info("🧹 Cleaning up temporary files...")
        
        temp_patterns = [
            "tmp/automation_capture_*.png",
            "tmp/screenshot_*.png",
            "tmp/window_*.png",
            "logs/*.lock",
            ".automation_running"
        ]
        
        project_root = Path(__file__).parent.parent
        cleaned_count = 0
        
        for pattern in temp_patterns:
            for file_path in project_root.glob(pattern):
                try:
                    file_path.unlink()
                    cleaned_count += 1
                    if self.verbose:
                        self.logger.debug(f"   Deleted: {file_path}")
                except Exception as e:
                    if self.verbose:
                        self.logger.debug(f"   Failed to delete {file_path}: {e}")
        
        if cleaned_count > 0:
            self.logger.info(f"   🗑️  Removed {cleaned_count} temporary file(s)")
        else:
            self.logger.info("   ✅ No temporary files found")


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Terminate VS Code Chat Continue automation processes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python terminate_automation.py              # Graceful termination
    python terminate_automation.py --force      # Force kill all processes
    python terminate_automation.py --verbose    # Show detailed output
    python terminate_automation.py --cleanup    # Also clean temp files
        """
    )
    
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Use SIGKILL instead of SIGTERM (force termination)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '-c', '--cleanup',
        action='store_true',
        help='Also clean up temporary files'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be terminated without actually doing it'
    )
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    print("🛑 VS Code Chat Continue Automation Terminator")
    print("=" * 50)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No processes will be terminated")
        print()
    
    terminator = AutomationTerminator(
        verbose=args.verbose,
        force=args.force
    )
    
    if args.dry_run:
        # Just show what would be terminated
        processes = terminator.find_automation_processes()
        if processes:
            print(f"📋 Would terminate {len(processes)} process(es):")
            for pid, name, cmdline in processes:
                print(f"   PID {pid}: {name}")
                if args.verbose:
                    print(f"      Command: {cmdline[:80]}...")
        else:
            print("✅ No automation processes found")
        return 0
    
    try:
        success = terminator.terminate_all()
        
        if args.cleanup:
            print()
            terminator.cleanup_temp_files()
        
        print()
        if success:
            print("✅ All automation processes terminated successfully")
            return 0
        else:
            print("⚠️  Some processes could not be terminated")
            return 1
            
    except KeyboardInterrupt:
        print("\n❌ Termination interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
