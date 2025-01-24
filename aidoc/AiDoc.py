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
    def __init__(self, driver, enable_screenshots=False, enable_memory=False, 
                 enable_accessibility=False, enable_security=False, 
                 enable_storage=False, export_format=None):
        self.driver = driver
        self.enable_screenshots = enable_screenshots
        self.enable_memory = enable_memory
        self.enable_accessibility = enable_accessibility
        self.enable_security = enable_security
        self.enable_storage = enable_storage
        self.export_format = export_format
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

def main():
    parser = argparse.ArgumentParser(
        description='AgenTest aiDoc - Advanced Web Console Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=AGENTEST_BANNER)
    
    parser.add_argument('url', help='URL to analyze')
    parser.add_argument('-u', '--username', help='Username for authentication')
    parser.add_argument('-p', '--password', help='Password for authentication')
    parser.add_argument('--screenshots', action='store_true', help='Enable screenshot capture')
    parser.add_argument('--memory', action='store_true', help='Enable memory monitoring')
    parser.add_argument('--accessibility', action='store_true', help='Enable accessibility checks')
    parser.add_argument('--security', action='store_true', help='Enable security analysis')
    parser.add_argument('--storage', action='store_true', help='Enable storage inspection')
    parser.add_argument('--export', choices=['html', 'json'], help='Export format')
    
    args = parser.parse_args()
    
    return main_impl(args.url, args.username, args.password,
                    enable_screenshots=args.screenshots,
                    enable_memory=args.memory,
                    enable_accessibility=args.accessibility,
                    enable_security=args.security,
                    enable_storage=args.storage,
                    export_format=args.export)

def main_impl(url, username=None, password=None, **kwargs):
    """Implementation of the main functionality"""
    start_time = time.time()
    print(AGENTEST_BANNER)
    
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--v=1')
    chrome_options.set_capability('goog:loggingPrefs', {
        'browser': 'ALL',
        'performance': 'ALL',
        'network': 'ALL'
    })

    try:
        # Initialize the Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
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
        print(f"\n{Colors.CYAN}Visiting {url}...{Colors.ENDC}")
        page_load_start = time.time()
        driver.get(url)
        page_load_time = time.time() - page_load_start
        
        # Handle login if credentials are provided
        login_time = None
        if username and password:
            try:
                print(f"\n{Colors.YELLOW}Attempting login...{Colors.ENDC}")
                login_start = time.time()
                
                # Wait for username field and login form
                username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
                password_field = driver.find_element(By.NAME, "password")
                
                # Fill in credentials
                username_field.send_keys(username)
                password_field.send_keys(password)
                
                # Submit the form
                password_field.submit()
                print(f"{Colors.GREEN}Login form submitted...{Colors.ENDC}")
                
                # Wait for page to load after login
                try:
                    wait.until(EC.staleness_of(username_field))
                    login_time = time.time() - login_start
                    print(f"{Colors.GREEN}Page reloaded after login... ({login_time:.2f}s){Colors.ENDC}")
                except TimeoutException:
                    print(f"{Colors.YELLOW}Warning: Page did not reload after login attempt{Colors.ENDC}")
                
            except Exception as e:
                print(f"\n{Colors.RED}Login failed: {str(e)}{Colors.ENDC}")
                print(f"{Colors.RED}Stack trace:\n{traceback.format_exc()}{Colors.ENDC}")

        # Collect console logs and run advanced features
        print(f"\n{Colors.BLUE}Running analysis...{Colors.ENDC}")
        
        # Basic console logs
        for log_entry in driver.get_log('browser'):
            console_handler.add_log(log_entry)
        
        # Advanced features
        if advanced.enable_screenshots and console_handler.logs:
            advanced.results['screenshots'] = advanced.capture_screenshot(len(console_handler.logs))
            
        if advanced.enable_memory:
            advanced.results['memory'] = advanced.get_memory_usage()
            
        if advanced.enable_accessibility:
            advanced.results['accessibility'] = advanced.check_accessibility()
            
        if advanced.enable_security:
            advanced.results['security'] = advanced.analyze_security_headers()
            
        if advanced.enable_storage:
            advanced.results['storage'] = advanced.inspect_storage()
        
        # Capture final state
        final_state = capture_page_state(driver, url)
        total_time = time.time() - start_time
        
        # Prepare report data
        page_info = {
            'url': url,
            'title': final_state['title'],
            'timing': {
                'page_load': page_load_time,
                'login': login_time,
                'total': total_time
            }
        }
        
        # Export results if requested
        if advanced.export_format:
            advanced.export_results(console_handler.logs, page_info)
        
        # Print detailed report
        print(f"\n{Colors.CYAN}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}DETAILED ANALYSIS REPORT{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*80}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}1. Timing Information:{Colors.ENDC}")
        print(f"{Colors.BOLD}Initial Page Load:{Colors.ENDC} {page_load_time:.2f}s")
        if login_time:
            print(f"{Colors.BOLD}Login Process:{Colors.ENDC} {login_time:.2f}s")
        print(f"{Colors.BOLD}Total Analysis Time:{Colors.ENDC} {total_time:.2f}s")
        
        print(f"\n{Colors.BOLD}2. Page Information:{Colors.ENDC}")
        print(f"{Colors.BOLD}Initial URL:{Colors.ENDC} {url}")
        print(f"{Colors.BOLD}Final URL:{Colors.ENDC} {final_state['url']}")
        print(f"{Colors.BOLD}Page Title:{Colors.ENDC} {final_state['title']}")
        
        print(f"\n{Colors.BOLD}3. Console Errors and Warnings:{Colors.ENDC}")
        print(console_handler.get_formatted_logs())
        
        if advanced.results:
            print(f"\n{Colors.BOLD}4. Advanced Analysis Results:{Colors.ENDC}")
            
            if 'memory' in advanced.results:
                memory = advanced.results['memory']
                print(f"\n{Colors.BOLD}Memory Usage:{Colors.ENDC}")
                print(f"RSS: {memory['rss']:.2f} MB")
                print(f"VMS: {memory['vms']:.2f} MB")
                print(f"Percent: {memory['percent']:.1f}%")
            
            if 'security' in advanced.results:
                headers = advanced.results['security']
                print(f"\n{Colors.BOLD}Security Headers:{Colors.ENDC}")
                for header, value in headers.items():
                    status = "✓" if value != "Not Set" else "✗"
                    color = Colors.GREEN if value != "Not Set" else Colors.RED
                    print(f"{color}{status} {header}: {value}{Colors.ENDC}")
            
            if 'storage' in advanced.results:
                storage = advanced.results['storage']
                print(f"\n{Colors.BOLD}Storage Information:{Colors.ENDC}")
                print(f"Cookies: {len(storage['cookies'])} found")
                print(f"LocalStorage Items: {len(storage['localStorage'])} found")
        
    except Exception as e:
        print(f"\n{Colors.RED}An error occurred: {str(e)}{Colors.ENDC}")
        print(f"{Colors.RED}Stack trace:\n{traceback.format_exc()}{Colors.ENDC}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == '__main__':
    main()
