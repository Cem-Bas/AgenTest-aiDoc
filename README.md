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
agentest-aidoc https://example.com

# With authentication
agentest-aidoc https://example.com -u username -p password
```

### Advanced Analysis
```bash
# Comprehensive analysis with all features
agentest-aidoc https://example.com \
    --screenshots \
    --memory \
    --security \
    --storage \
    --accessibility \
    --export html
```

### 🎛️ Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--screenshots` | Capture screenshots on errors | False |
| `--memory` | Monitor memory usage | False |
| `--accessibility` | Run accessibility checks | False |
| `--security` | Analyze security headers | False |
| `--storage` | Inspect cookies & localStorage | False |
| `--export` | Export format (html/json) | None |

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
