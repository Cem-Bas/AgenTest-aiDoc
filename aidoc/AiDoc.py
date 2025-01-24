import sys
import argparse
import json
import time
import os
import base64
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import traceback
import requests
import psutil
from axe_selenium_python import Axe
import html

# ANSI Color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    MAGENTA = '\033[35m'

AGENTEST_BANNER = f"""{Colors.CYAN}
    ___                     _______        __  
   /   |  ____ ____  ____  /_  __/__  ___ / /_ 
  / /| | / __ `/ _ \\/ __ \\  / / / _ \\(_-</ __/ 
 / ___ |/ /_/ /  __/ / / / / / /  __/___/\\__/  
/_/  |_|\\__, /\\___/_/ /_/ /_/  \\___/          
       /____/                      {Colors.MAGENTA}aiDoc{Colors.ENDC}

{Colors.BLUE}[ AgenTest Console Error Detection System ]{Colors.ENDC}
"""

class ErrorCategory:
    AUTHENTICATION = 'Authentication'
    NETWORK = 'Network'
    JAVASCRIPT = 'JavaScript'
    RESOURCE = 'Resource'
    DOM = 'DOM'
    OTHER = 'Other'

    @staticmethod
    def categorize(error_message):
        message = error_message.lower()
        if any(term in message for term in ['login', 'auth', 'credential', 'permission']):
            return ErrorCategory.AUTHENTICATION
        elif any(term in message for term in ['net::', 'failed to load', 'network', 'fetch']):
            return ErrorCategory.NETWORK
        elif any(term in message for term in ['undefined', 'null', 'cannot read property', 'is not a function']):
            return ErrorCategory.JAVASCRIPT
        elif any(term in message for term in ['404', 'resource', 'not found', 'failed to load resource']):
            return ErrorCategory.RESOURCE
        elif any(term in message for term in ['querySelector', 'element', 'node', 'document']):
            return ErrorCategory.DOM
        return ErrorCategory.OTHER

class ConsoleLogHandler:
    def __init__(self):
        self.logs = []
        self.error_categories = {}
        
    def add_log(self, log_entry):
        self.logs.append(log_entry)
        if log_entry.get('level') in ['SEVERE', 'ERROR', 'WARNING']:
            category = ErrorCategory.categorize(log_entry.get('message', ''))
            self.error_categories[category] = self.error_categories.get(category, 0) + 1
        
    def get_formatted_logs(self):
        formatted = []
        for log in self.logs:
            level = log.get('level', 'INFO')
            message = log.get('message', '')
            source = log.get('source', '')
            timestamp = log.get('timestamp', '')
            
            if level in ['SEVERE', 'ERROR', 'WARNING']:
                category = ErrorCategory.categorize(message)
                formatted.append(f"\n{Colors.YELLOW}{'='*80}{Colors.ENDC}")
                formatted.append(f"{Colors.BOLD}LEVEL:{Colors.ENDC} {Colors.RED if level in ['SEVERE', 'ERROR'] else Colors.YELLOW}{level}{Colors.ENDC}")
                formatted.append(f"{Colors.BOLD}CATEGORY:{Colors.ENDC} {Colors.CYAN}{category}{Colors.ENDC}")
                formatted.append(f"{Colors.BOLD}SOURCE:{Colors.ENDC} {Colors.BLUE}{source}{Colors.ENDC}")
                formatted.append(f"{Colors.BOLD}TIMESTAMP:{Colors.ENDC} {datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                formatted.append(f"{Colors.BOLD}MESSAGE:{Colors.ENDC} {message}")
                formatted.append(f"{Colors.YELLOW}{'='*80}{Colors.ENDC}")
        
        if self.error_categories:
            formatted.append(f"\n{Colors.BOLD}Error Summary by Category:{Colors.ENDC}")
            for category, count in self.error_categories.items():
                formatted.append(f"{Colors.CYAN}{category}:{Colors.ENDC} {count} error(s)")
        
        return '\n'.join(formatted) if formatted else f"{Colors.GREEN}No significant console logs found.{Colors.ENDC}"

class AdvancedFeatures:
    def __init__(self, driver, **kwargs):
        self.driver = driver
        self.enable_screenshots = kwargs.get('enable_screenshots', False)
        self.enable_memory = kwargs.get('enable_memory', False)
        self.enable_accessibility = kwargs.get('enable_accessibility', False)
        self.enable_security = kwargs.get('enable_security', False)
        self.enable_storage = kwargs.get('enable_storage', False)
        self.export_format = kwargs.get('export_format')
        self.results = {}

    def capture_screenshot(self, error_count):
        """Capture screenshot when errors occur"""
        if not self.enable_screenshots:
            return None
            
        try:
            screenshot_dir = "reports/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{screenshot_dir}/error_{error_count}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            print(f"{Colors.GREEN}Screenshot saved: {filename}{Colors.ENDC}")
            return filename
        except Exception as e:
            print(f"{Colors.RED}Failed to capture screenshot: {str(e)}{Colors.ENDC}")
            return None

    def get_memory_usage(self):
        """Monitor memory usage"""
        if not self.enable_memory:
            return None
            
        try:
            process = psutil.Process(os.getpid())
            memory_info = {
                'rss': process.memory_info().rss / 1024 / 1024,  # MB
                'vms': process.memory_info().vms / 1024 / 1024,  # MB
                'percent': process.memory_percent()
            }
            return memory_info
        except Exception as e:
            print(f"{Colors.RED}Failed to get memory usage: {str(e)}{Colors.ENDC}")
            return None

    def check_accessibility(self):
        """Perform accessibility checks using axe-core"""
        if not self.enable_accessibility:
            return None
            
        try:
            axe = Axe(self.driver)
            axe.inject()
            results = axe.run()
            
            violations = results['violations']
            if violations:
                print(f"\n{Colors.BOLD}Accessibility Issues Found:{Colors.ENDC}")
                for violation in violations:
                    print(f"\n{Colors.YELLOW}Rule: {violation['id']}{Colors.ENDC}")
                    print(f"Impact: {violation['impact']}")
                    print(f"Description: {violation['description']}")
                    
            return results
        except Exception as e:
            print(f"{Colors.RED}Failed to perform accessibility check: {str(e)}{Colors.ENDC}")
            return None

    def analyze_security_headers(self):
        """Analyze security headers of the page"""
        if not self.enable_security:
            return None
            
        try:
            url = self.driver.current_url
            response = requests.get(url)
            headers = response.headers
            
            security_headers = {
                'Strict-Transport-Security': headers.get('Strict-Transport-Security', 'Not Set'),
                'Content-Security-Policy': headers.get('Content-Security-Policy', 'Not Set'),
                'X-Frame-Options': headers.get('X-Frame-Options', 'Not Set'),
                'X-Content-Type-Options': headers.get('X-Content-Type-Options', 'Not Set'),
                'X-XSS-Protection': headers.get('X-XSS-Protection', 'Not Set')
            }
            
            return security_headers
        except Exception as e:
            print(f"{Colors.RED}Failed to analyze security headers: {str(e)}{Colors.ENDC}")
            return None

    def inspect_storage(self):
        """Inspect cookies and localStorage"""
        if not self.enable_storage:
            return None
            
        try:
            cookies = self.driver.get_cookies()
            local_storage = self.driver.execute_script("""
                let items = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
            """)
            
            return {
                'cookies': cookies,
                'localStorage': local_storage
            }
        except Exception as e:
            print(f"{Colors.RED}Failed to inspect storage: {str(e)}{Colors.ENDC}")
            return None

    def analyze(self, error_categories):
        """Run all enabled analysis features"""
        if self.enable_screenshots and error_categories:
            self.results['screenshots'] = self.capture_screenshot(len(error_categories))
            
        if self.enable_memory:
            self.results['memory'] = self.get_memory_usage()
            
        if self.enable_accessibility:
            self.results['accessibility'] = self.check_accessibility()
            
        if self.enable_security:
            self.results['security'] = self.analyze_security_headers()
            
        if self.enable_storage:
            self.results['storage'] = self.inspect_storage()

    def export_results(self, console_logs, page_info):
        """Export results in specified format"""
        if not self.export_format:
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            if self.export_format.lower() == 'json':
                json_dir = f"{reports_dir}/json"
                os.makedirs(json_dir, exist_ok=True)
                filename = f"{json_dir}/report_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump({
                        'page_info': page_info,
                        'console_logs': console_logs,
                        'advanced_features': self.results
                    }, f, indent=2)
                    
            elif self.export_format.lower() == 'html':
                html_dir = f"{reports_dir}/html"
                os.makedirs(html_dir, exist_ok=True)
                filename = f"{html_dir}/report_{timestamp}.html"
                with open(filename, 'w') as f:
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>AgenTest.ai Report</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 20px; }}
                            .error {{ color: red; }}
                            .warning {{ color: orange; }}
                            .success {{ color: green; }}
                            .section {{ margin: 20px 0; padding: 10px; border: 1px solid #ccc; }}
                        </style>
                    </head>
                    <body>
                        <h1>AgenTest.ai Analysis Report</h1>
                        <div class="section">
                            <h2>Page Information</h2>
                            <pre>{html.escape(json.dumps(page_info, indent=2))}</pre>
                        </div>
                        <div class="section">
                            <h2>Console Logs</h2>
                            <pre>{html.escape(json.dumps(console_logs, indent=2))}</pre>
                        </div>
                        <div class="section">
                            <h2>Advanced Analysis</h2>
                            <pre>{html.escape(json.dumps(self.results, indent=2))}</pre>
                        </div>
                    </body>
                    </html>
                    """
                    f.write(html_content)
                    
            print(f"{Colors.GREEN}Report exported to: {filename}{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.RED}Failed to export results: {str(e)}{Colors.ENDC}")

def capture_page_state(driver, url):
    """Capture detailed information about the current page state"""
    state = {
        "url": driver.current_url,
        "title": driver.title,
        "page_source_excerpt": driver.page_source[:1000] + "..." if len(driver.page_source) > 1000 else driver.page_source
    }
    
    # Capture network state using JavaScript
    network_state = driver.execute_script("""
        const performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {};
        const network = performance.getEntriesByType ? performance.getEntriesByType("resource") : [];
        return network.map(entry => ({
            name: entry.name,
            duration: entry.duration,
            startTime: entry.startTime,
            responseEnd: entry.responseEnd,
            initiatorType: entry.initiatorType
        }));
    """)
    
    state["network_requests"] = network_state
    
    # Capture JavaScript errors
    js_errors = driver.execute_script("""
        return window.jsErrors || [];
    """)
    
    state["js_errors"] = js_errors
    
    return state

def inject_error_listeners(driver):
    """Inject JavaScript to capture errors and unhandled rejections"""
    driver.execute_script("""
        window.jsErrors = [];
        window.addEventListener('error', function(event) {
            window.jsErrors.push({
                type: 'error',
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error ? event.error.stack : null,
                timestamp: new Date().toISOString()
            });
        });
        window.addEventListener('unhandledrejection', function(event) {
            window.jsErrors.push({
                type: 'unhandledrejection',
                message: event.reason,
                timestamp: new Date().toISOString()
            });
        });
    """)

def print_report(page_info, console_handler, total_time):
    print(f"\n{Colors.CYAN}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}DETAILED ANALYSIS REPORT{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*80}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}1. Timing Information:{Colors.ENDC}")
    print(f"{Colors.BOLD}Page Load Time:{Colors.ENDC} {page_info['load_time']:.2f}s")
    print(f"{Colors.BOLD}Total Analysis Time:{Colors.ENDC} {total_time:.2f}s")
    
    print(f"\n{Colors.BOLD}2. Page Information:{Colors.ENDC}")
    print(f"{Colors.BOLD}URL:{Colors.ENDC} {page_info['url']}")
    print(f"{Colors.BOLD}Page Title:{Colors.ENDC} {page_info['title']}")
    
    print(f"\n{Colors.BOLD}3. Console Errors and Warnings:{Colors.ENDC}")
    print(console_handler.get_formatted_logs())

def main():
    parser = argparse.ArgumentParser(
        description='AgenTest aiDoc - Advanced Web Console Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=AGENTEST_BANNER)
    
    parser.add_argument('url', help='URL to analyze')
    parser.add_argument('--interactive', action='store_true', help='Launch browser in interactive mode for manual login')
    parser.add_argument('--wait-after-login', type=int, default=10, help='Seconds to wait after login before analysis (default: 10)')
    parser.add_argument('--screenshots', action='store_true', help='Enable screenshot capture')
    parser.add_argument('--memory', action='store_true', help='Enable memory monitoring')
    parser.add_argument('--accessibility', action='store_true', help='Enable accessibility checks')
    parser.add_argument('--security', action='store_true', help='Enable security analysis')
    parser.add_argument('--storage', action='store_true', help='Enable storage inspection')
    parser.add_argument('--export', choices=['html', 'json'], help='Export format')
    
    args = parser.parse_args()
    
    return main_impl(args.url,
                    interactive=args.interactive,
                    wait_after_login=args.wait_after_login,
                    enable_screenshots=args.screenshots,
                    enable_memory=args.memory,
                    enable_accessibility=args.accessibility,
                    enable_security=args.security,
                    enable_storage=args.storage,
                    export_format=args.export)

def main_impl(url, **kwargs):
    """Implementation of the main functionality"""
    start_time = time.time()
    print(AGENTEST_BANNER)
    
    # Initialize Chrome options
    chrome_options = Options()
    if not kwargs.get('interactive', False):
        chrome_options.add_argument('--headless')  # Run in headless mode only if not interactive
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Create reports directory if it doesn't exist
    os.makedirs('reports/screenshots', exist_ok=True)
    os.makedirs('reports/html', exist_ok=True)
    os.makedirs('reports/json', exist_ok=True)
    
    driver = None
    try:
        # Initialize WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        # Initialize console log handler
        console_handler = ConsoleLogHandler()
        
        # Initialize advanced features
        advanced = AdvancedFeatures(
            driver,
            enable_screenshots=kwargs.get('enable_screenshots', False),
            enable_memory=kwargs.get('enable_memory', False),
            enable_accessibility=kwargs.get('enable_accessibility', False),
            enable_security=kwargs.get('enable_security', False),
            enable_storage=kwargs.get('enable_storage', False),
            export_format=kwargs.get('export_format')
        )
        
        # Visit the URL
        print(f"\nVisiting {url}...")
        load_start = time.time()
        driver.get(url)
        load_time = time.time() - load_start
        
        if kwargs.get('interactive', False):
            print(f"\n{Colors.YELLOW}Interactive mode enabled. Please log in manually if needed.{Colors.ENDC}")
            print(f"{Colors.YELLOW}Waiting {kwargs.get('wait_after_login', 10)} seconds after login...{Colors.ENDC}")
            time.sleep(kwargs.get('wait_after_login', 10))
            print(f"{Colors.GREEN}Proceeding with analysis...{Colors.ENDC}")
        
        print("\nRunning analysis...")
        
        # Inject error listeners
        inject_error_listeners(driver)
        
        # Capture the current state of the page
        page_info = capture_page_state(driver, url)
        page_info['load_time'] = load_time
        
        # Get console logs
        logs = driver.get_log('browser')
        for log in logs:
            console_handler.add_log(log)
        
        # Run advanced analysis
        advanced.analyze(console_handler.error_categories)
        
        # Generate report
        total_time = time.time() - start_time
        print_report(page_info, console_handler, total_time)
        
        # Export results if requested
        if kwargs.get('export_format'):
            advanced.export_results(console_handler.get_formatted_logs(), page_info)
        
        return 0
        
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.ENDC}")
        traceback.print_exc()
        return 1
        
    finally:
        if driver and not kwargs.get('interactive', False):
            driver.quit()

if __name__ == '__main__':
    main()
