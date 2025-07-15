#!/usr/bin/env python3
"""
Test script to verify the project structure and basic functionality.
"""

import sys
from pathlib import Path


class ProjectVerificationTest:
    """Test class to verify project structure and functionality."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.errors = []
        self.warnings = []
        self.passed_tests = 0
        self.total_tests = 0

    def run_all_tests(self) -> bool:
        """Run all verification tests."""
        print("🔍 Starting Project Verification Tests...")
        print("=" * 50)

        # Structure tests
        self.test_directory_structure()
        self.test_required_files()
        self.test_python_files_syntax()

        # Configuration tests
        self.test_pyproject_toml()
        self.test_requirements_files()

        # Documentation tests
        self.test_documentation_files()

        # GitHub workflow tests
        self.test_github_files()

        # Basic import tests
        self.test_basic_imports()

        # Print results
        self.print_results()

        return len(self.errors) == 0

    def test_directory_structure(self):
        """Test that required directories exist."""
        self.total_tests += 1
        required_dirs = [
            "src",
            "tests",
            "docs",
            "scripts",
            "config",
            "logs",
            "tmp",
            ".github",
            ".copilot",
        ]

        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)

        if missing_dirs:
            dirs_str = ", ".join(missing_dirs)
            self.errors.append(f"Missing directories: {dirs_str}")
        else:
            self.passed_tests += 1
            print("✅ Directory structure test passed")

    def test_required_files(self):
        """Test that required files exist."""
        self.total_tests += 1
        required_files = [
            "README.md",
            "CHANGELOG.md",
            "WORKFLOW.md",
            "PROJECT_GOALS.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "pyproject.toml",
            "requirements.txt",
            "requirements-dev.txt",
            ".gitignore",
            ".editorconfig",
            "run.sh",
        ]

        missing_files = []
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                missing_files.append(file_name)

        if missing_files:
            self.errors.append(f"Missing files: {', '.join(missing_files)}")
        else:
            self.passed_tests += 1
            print("✅ Required files test passed")

    def test_python_files_syntax(self):
        """Test Python files for syntax errors."""
        self.total_tests += 1
        python_files = list(self.project_root.rglob("*.py"))
        syntax_errors = []

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    compile(f.read(), py_file, "exec")
            except SyntaxError as e:
                syntax_errors.append(f"{py_file}: {e}")
            except Exception as e:
                self.warnings.append(f"Could not check {py_file}: {e}")

        if syntax_errors:
            self.errors.append(f"Python syntax errors: {syntax_errors}")
        else:
            self.passed_tests += 1
            files_count = len(python_files)
            print(f"✅ Python syntax test passed ({files_count} files checked)")

    def test_pyproject_toml(self):
        """Test pyproject.toml structure."""
        self.total_tests += 1
        pyproject_path = self.project_root / "pyproject.toml"

        if not pyproject_path.exists():
            self.errors.append("pyproject.toml not found")
            return

        try:
            import tomllib

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            required_sections = ["build-system", "project", "tool"]
            missing_sections = [s for s in required_sections if s not in data]

            if missing_sections:
                sections_str = ", ".join(missing_sections)
                error_msg = f"pyproject.toml missing sections: {sections_str}"
                self.errors.append(error_msg)
            else:
                self.passed_tests += 1
                print("✅ pyproject.toml structure test passed")

        except Exception as e:
            self.errors.append(f"pyproject.toml parsing error: {e}")

    def test_requirements_files(self):
        """Test requirements files."""
        self.total_tests += 1
        req_files = ["requirements.txt", "requirements-dev.txt"]
        errors = []

        for req_file in req_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                try:
                    with open(req_path, "r") as f:
                        content = f.read().strip()
                        if not content:
                            errors.append(f"{req_file} is empty")
                except Exception as e:
                    errors.append(f"Error reading {req_file}: {e}")
            else:
                errors.append(f"{req_file} not found")

        if errors:
            self.errors.extend(errors)
        else:
            self.passed_tests += 1
            print("✅ Requirements files test passed")

    def test_documentation_files(self):
        """Test documentation files content."""
        self.total_tests += 1
        doc_files = ["README.md", "WORKFLOW.md", "PROJECT_GOALS.md", "CONTRIBUTING.md"]
        errors = []

        for doc_file in doc_files:
            doc_path = self.project_root / doc_file
            if doc_path.exists():
                try:
                    with open(doc_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if len(content) < 100:  # Minimal content check
                            errors.append(f"{doc_file} has minimal content")
                except Exception as e:
                    errors.append(f"Error reading {doc_file}: {e}")
            else:
                errors.append(f"{doc_file} not found")

        if errors:
            self.warnings.extend(errors)  # Documentation warnings, not errors
            self.passed_tests += 1
            print("⚠️  Documentation files test passed with warnings")
        else:
            self.passed_tests += 1
            print("✅ Documentation files test passed")

    def test_github_files(self):
        """Test GitHub workflow and template files."""
        self.total_tests += 1
        github_files = [
            ".github/workflows/ci.yml",
            ".github/workflows/release.yml",
            ".github/workflows/docs.yml",
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/feature_request.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/CODEOWNERS",
        ]

        missing_files = []
        for file_path in github_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            self.warnings.extend(missing_files)  # GitHub files are warnings
            self.passed_tests += 1
            print("⚠️  GitHub files test passed with warnings")
        else:
            self.passed_tests += 1
            print("✅ GitHub files test passed")

    def test_basic_imports(self):
        """Test basic imports of main modules."""
        self.total_tests += 1
        try:
            # Add src to path for imports
            src_path = str(self.project_root / "src")
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            # Test main imports - imports are checked, not used
            import main  # noqa: F401
            from core import automation_engine, window_detector  # noqa: F401
            from utils import logger, screen_capture  # noqa: F401

            self.passed_tests += 1
            print("✅ Basic imports test passed")

        except Exception as e:
            self.errors.append(f"Import error: {e}")

    def print_results(self):
        """Print test results summary."""
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)

        print(f"Tests Passed: {self.passed_tests}/{self.total_tests}")
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
        else:
            success_rate = 0
        print(f"Success Rate: {success_rate:.1f}%")

        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        if not self.errors and not self.warnings:
            print("\n🎉 All tests passed! Project structure is perfect.")
        elif not self.errors:
            print("\n✅ All critical tests passed! Some warnings to review.")
        else:
            print("\n❌ Some tests failed. Please fix the errors above.")


def main():
    """Main test execution."""
    verifier = ProjectVerificationTest()
    success = verifier.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
