# 🔍 AgenTest aiDoc - Advanced Web Console Analyzer

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

*A powerful web console analysis tool for modern web applications*

[Features](#-features) •
[Installation](#-installation) •
[Usage](#-usage) •
[Documentation](#-documentation) •
[Contributing](#-contributing)

</div>

---

## ✨ Features

### 🎯 Core Capabilities
- **Console Error Analysis**
  - 📊 Real-time error capture and categorization
  - ⏱️ Precise timestamp tracking
  - 🔍 Detailed stack trace examination
  - 📝 Error grouping by type (Authentication, JavaScript, Network, etc.)

### 🚀 Advanced Features
<table>
<tr>
<td>

#### 📸 Visual Analysis
- Screenshot capture on errors
- Visual regression tracking
- Error highlighting

</td>
<td>

#### 🔒 Security Analysis
- Security header inspection
- Cookie analysis
- localStorage monitoring

</td>
</tr>
<tr>
<td>

#### 📊 Performance Metrics
- Memory usage tracking
- Load time analysis
- Network request monitoring

</td>
<td>

#### ♿ Accessibility
- WCAG compliance checking
- Accessibility score
- Improvement suggestions

</td>
</tr>
</table>

### 🤝 Interactive Login Feature
- **Interactive Mode**: Launch a visible browser window for manual login
- **Wait After Login**: Time to wait after login before starting analysis (default: 10)

## 🚀 Installation

### Quick Start
```bash
# Clone the repository
git clone https://github.com/agentest/aidoc.git
cd aidoc

# Run the installation script
./install.sh
```

### Manual Installation
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## 🎮 Usage

### Basic Analysis
```bash
# Simple URL analysis
aidoc https://example.com

# With authentication
aidoc https://example.com -u username -p password
```

### Advanced Analysis
```bash
# Comprehensive analysis with all features
aidoc https://example.com \
    --screenshots \
    --memory \
    --security \
    --storage \
    --accessibility \
    --export html
```

### Analyzing Login-Required Sites

> **🔒 Security Notice**
> 
> AgenTest aiDoc prioritizes your security:
> - No authentication data is ever logged or stored
> - Login is handled through a manual interactive browser session
> - Credentials remain solely in your control
> - No session data is persisted after analysis
> - Reports and screenshots never contain sensitive authentication information

For sites that require authentication, use interactive mode:
```bash
aidoc https://mail.google.com --interactive --screenshots --export html
```

Interactive mode options:
- `--interactive`: Launch a visible browser window for manual login
- `--wait-after-login <seconds>`: Time to wait after login before starting analysis (default: 10)

Example with custom wait time:
```bash
aidoc https://mail.google.com --interactive --wait-after-login 15 --screenshots --export html
```

### Best Practices for Secure Analysis

When analyzing login-protected sites:
1. Always use interactive mode (`--interactive`)
2. Log in manually through the browser window
3. Never share exported reports containing sensitive data
4. Close the browser window after analysis
5. Use private/incognito mode if needed (coming soon)

### 🎛️ Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--screenshots` | Capture screenshots on errors | False |
| `--memory` | Monitor memory usage | False |
| `--accessibility` | Run accessibility checks | False |
| `--security` | Analyze security headers | False |
| `--storage` | Inspect cookies & localStorage | False |
| `--export` | Export format (html/json) | None |
| `--interactive` | Launch a visible browser window for manual login | False |
| `--wait-after-login` | Time to wait after login before starting analysis | 10 |

## 📁 Output Structure

```
reports/
├── 📸 screenshots/    # Error screenshots
├── 📄 html/          # HTML reports
└── 📊 json/          # JSON reports
```

## 🔧 Requirements

### System Requirements
- Python 3.8 or higher
- Google Chrome browser

### Python Packages
```txt
selenium>=4.0.0
webdriver-manager>=3.8.0
requests>=2.28.0
psutil>=5.9.0
axe-selenium-python>=2.1.6
```

## 👩‍💻 Development

### Setting Up Development Environment
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

### Code Style
We use [Black](https://github.com/psf/black) for code formatting:
```bash
black aidoc/
```

## 🤝 Contributing

We love your input! We want to make contributing to AiDoc as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

### Steps to Contribute
1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

<table>
<tr>
<td>
<strong>📧 Email:</strong><br>
support@agentest.ai
</td>
<td>
<strong>💬 Discord:</strong><br>
Join our <a href="https://discord.gg/agentest">community</a>
</td>
<td>
<strong>🐛 Issues:</strong><br>
Report on <a href="https://github.com/agentest/aidoc/issues">GitHub</a>
</td>
</tr>
</table>

---

<div align="center">
Made with ❤️ by <a href="https://agentest.ai">AgenTest.ai</a>
</div>
