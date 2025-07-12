# Contributing to VS Code Chat Continue Automation

Thank you for your interest in contributing to VS Code Chat Continue Automation! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Ways to Contribute

1. **🐛 Bug Reports**: Report issues and bugs
2. **✨ Feature Requests**: Suggest new features and improvements
3. **💻 Code Contributions**: Submit bug fixes and new features
4. **📚 Documentation**: Improve documentation and guides
5. **🧪 Testing**: Help with testing across different platforms
6. **🎨 Design**: UI/UX improvements and design suggestions

## 🚀 Getting Started

### Development Setup

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/vscode-chat-continue.git
   cd vscode-chat-continue
   ```

2. **Set Up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or: venv\\Scripts\\activate  # Windows
   
   pip install -e \".[dev]\"
   ```

3. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

4. **Verify Setup**
   ```bash
   pytest
   ./scripts/dev.sh lint
   ```

### Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run all tests
   pytest
   
   # Run specific test categories
   pytest tests/unit/
   pytest tests/integration/
   
   # Check code quality
   ./scripts/dev.sh lint
   ./scripts/dev.sh format
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m \"feat: add amazing new feature\"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create PR through GitHub interface
   ```

## 📋 Contribution Guidelines

### Code Standards

- **Python Version**: 3.8+ with type hints
- **Code Style**: Black formatting (100 character line length)
- **Linting**: Pass Pylint with score 8.5+
- **Type Checking**: Pass MyPy strict mode
- **Testing**: 80%+ code coverage

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

**Examples:**
```
feat: add multi-language OCR support
fix: resolve memory leak in screen capture
docs: update installation instructions
refactor: simplify configuration management
test: add integration tests for button detection
```

### Pull Request Guidelines

1. **PR Title**: Use conventional commit format
2. **Description**: Clear explanation of changes and motivation
3. **Size**: Keep PRs focused and reasonably sized (<400 lines)
4. **Testing**: Include tests for new functionality
5. **Documentation**: Update docs for user-facing changes

### Code Review Process

All contributions go through code review:

1. **Automated Checks**: CI/CD pipeline must pass
2. **Manual Review**: At least one maintainer approval
3. **Testing**: Reviewer may test changes locally
4. **Feedback**: Address review comments promptly

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Fast, isolated unit tests
├── integration/    # Component interaction tests
├── automation/     # End-to-end automation tests
├── manual/         # Manual testing procedures
└── fixtures/       # Test data and mocks
```

### Writing Tests

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Naming**: Use descriptive test names
4. **Coverage**: Aim for 80%+ coverage on new code
5. **Performance**: Include performance tests for critical paths

### Running Tests

```bash
# All tests
pytest

# Specific categories
pytest tests/unit/
pytest tests/integration/

# With coverage
pytest --cov=src --cov-report=html

# Performance tests
pytest --benchmark-only
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear Description**: What happened vs. what was expected
2. **Reproduction Steps**: Step-by-step instructions
3. **Environment**: OS, Python version, VS Code version
4. **Logs**: Relevant error messages and logs
5. **Screenshots**: If applicable for UI issues

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

## ✨ Feature Requests

For feature requests, please provide:

1. **Problem Statement**: What problem does this solve?
2. **Proposed Solution**: How should it work?
3. **Use Cases**: Who would benefit and how?
4. **Implementation Ideas**: Technical approach (if any)

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

## 📚 Documentation Contributions

Documentation improvements are always welcome:

1. **README**: Installation, usage, and quick start
2. **API Docs**: Code documentation and examples
3. **User Guides**: Tutorials and how-to guides
4. **Developer Docs**: Architecture and contribution guides

### Documentation Standards

- **Clarity**: Write for your audience's skill level
- **Examples**: Include practical examples
- **Structure**: Use consistent formatting and structure
- **Accuracy**: Keep documentation up-to-date with code

## 🎨 Design Contributions

For UI/UX improvements:

1. **User Research**: Understand user needs and pain points
2. **Design Principles**: Follow established design patterns
3. **Accessibility**: Ensure inclusive design practices
4. **Consistency**: Maintain visual and interaction consistency

## 🛡️ Security

### Reporting Security Issues

**Do NOT create public issues for security vulnerabilities.**

Instead:
1. Email security concerns to: security@example.com
2. Use GitHub's private vulnerability reporting
3. Follow responsible disclosure practices

### Security Guidelines

- Never commit secrets or credentials
- Validate all user inputs
- Follow secure coding practices
- Keep dependencies updated

## 📞 Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Technical discussions and Q&A
- **Slack/Discord**: Real-time community chat
- **Email**: Official announcements

### Code of Conduct

We follow the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please read it to understand expected behavior in our community.

### Getting Help

- **Documentation**: Check existing docs first
- **Search Issues**: Look for similar problems/questions
- **Ask Questions**: Use GitHub Discussions for help
- **Join Community**: Connect with other contributors

## 🎖️ Recognition

We value all contributions and recognize contributors through:

1. **Contributors List**: README acknowledgment
2. **Release Notes**: Feature/fix attribution
3. **Special Recognition**: Outstanding contributions
4. **Maintainer Invitation**: Long-term contributors

## 📋 Legal

### License Agreement

By contributing, you agree that your contributions will be licensed under the MIT License.

### Copyright

- Retain original copyright notices
- Add your copyright for substantial contributions
- Follow project licensing requirements

## 🚀 Advanced Contributing

### Becoming a Maintainer

Regular contributors may be invited to become maintainers:

1. **Consistent Contributions**: Regular, high-quality contributions
2. **Community Involvement**: Help other contributors
3. **Technical Expertise**: Deep understanding of the codebase
4. **Leadership**: Guide project direction and decisions

### Project Governance

- **Maintainers**: Core team with merge permissions
- **Contributors**: Community members who contribute
- **Users**: People who use the project

### Decision Making

- **Consensus**: Prefer collaborative decision making
- **Maintainer Vote**: When consensus isn't reached
- **Technical Decisions**: Based on merit and project goals
- **Community Input**: Actively seek user and contributor feedback

## 📈 Project Roadmap

See our [PROJECT_GOALS.md](PROJECT_GOALS.md) for:
- Short-term and long-term goals
- Feature roadmap and priorities
- Technical architecture evolution
- Community growth plans

## 🙏 Thank You

Thank you for considering contributing to VS Code Chat Continue Automation! Your contributions make this project better for everyone.

---

*This document is living and evolves with the project. Suggestions for improvements are welcome!*
