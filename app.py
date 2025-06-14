from flask import Flask, request, render_template, send_from_directory, jsonify, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import os
import csv
import requests
import socket
import logging
import time
import threading
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from datetime import datetime
import json
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sniffer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'csv'}

# Initialize extensions
CORS(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def ensure_protocol(url):
    """Ensure URL has proper protocol."""
    if not url.startswith(('http://', 'https://')):
        return 'https://' + url
    return url

def validate_url(url):
    """Validate URL format and accessibility."""
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False

def get_ip_and_location(url):
    """Get IP address and geolocation with error handling."""
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        
        # Try to resolve IP
        try:
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            return 'N/A', 'N/A'
        
        # Get geolocation with timeout
        try:
            response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
            if response.status_code == 200:
                ip_info = response.json()
                lat = ip_info.get('lat', 'N/A')
                lon = ip_info.get('lon', 'N/A')
                location = f"{lat},{lon}"
                return ip_address, location
        except requests.RequestException:
            pass
        
        return ip_address, 'N/A'
    except Exception as e:
        logger.error(f"Error getting IP and location for {url}: {str(e)}")
        return 'N/A', 'N/A'

def check_url_status_and_get_title(urls, timeout=10):
    """Check URL status and get title with improved error handling."""
    valid_urls_and_titles = []
    
    if isinstance(urls, list):
        urls_list = urls
    else:
        try:
            with open(urls, 'r', encoding='utf-8') as infile:
                urls_list = infile.readlines()
        except Exception as e:
            logger.error(f"Error reading file {urls}: {str(e)}")
            return []
    
    def process_url(url):
        url = url.strip()
        if not url:
            return None
            
        url = ensure_protocol(url)
        
        if not validate_url(url):
            return (url, 'Invalid URL', 'Failed', 'N/A', 'N/A')
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
            
            if response.status_code == 200:
                try:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    title = soup.title.string.strip() if soup.title else 'No Title'
                    # Limit title length
                    title = title[:100] + '...' if len(title) > 100 else title
                except Exception:
                    title = 'No Title'
                
                ip_address, location = get_ip_and_location(url)
                return (url, title, 'Success', ip_address, location)
            else:
                return (url, 'No Title', f'Failed ({response.status_code})', 'N/A', 'N/A')
                
        except requests.Timeout:
            return (url, 'No Title', 'Timeout', 'N/A', 'N/A')
        except requests.RequestException as e:
            return (url, 'No Title', f'Error: {str(e)[:50]}', 'N/A', 'N/A')
        except Exception as e:
            logger.error(f"Unexpected error processing {url}: {str(e)}")
            return (url, 'No Title', 'Unexpected Error', 'N/A', 'N/A')
    
    # Process URLs with threading for better performance
    with threading.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_url, url) for url in urls_list]
        for future in futures:
            result = future.result()
            if result:
                valid_urls_and_titles.append(result)
    
    return valid_urls_and_titles

def fetch_subdomains(domain):
    """Fetch subdomains with improved error handling and multiple sources."""
    domain = domain.replace('http://', '').replace('https://', '').strip('/')
    subdomains = set()
    
    # Source 1: crt.sh
    try:
        crt_sh_url = f'https://crt.sh/?q=%25.{domain}&output=json'
        response = requests.get(crt_sh_url, timeout=10)
        if response.status_code == 200:
            for entry in response.json():
                name_value = entry['name_value']
                subdomains.update(name_value.split('\n'))
    except Exception as e:
        logger.error(f"Error fetching from crt.sh: {str(e)}")
    
    # Source 2: DNS enumeration
    try:
        common_subdomains = ['www', 'mail', 'ftp', 'admin', 'blog', 'dev', 'test', 'api', 'cdn', 'static']
        for sub in common_subdomains:
            try:
                full_domain = f"{sub}.{domain}"
                socket.gethostbyname(full_domain)
                subdomains.add(full_domain)
            except socket.gaierror:
                continue
    except Exception as e:
        logger.error(f"Error in DNS enumeration: {str(e)}")
    
    # Filter and clean subdomains
    filtered_subdomains = []
    for subdomain in subdomains:
        subdomain = subdomain.strip().lower()
        if subdomain and domain in subdomain and subdomain != domain:
            filtered_subdomains.append(subdomain)
    
    return list(set(filtered_subdomains))

def ensure_trailing_slash(url):
    """Ensure URL has trailing slash."""
    if not url.endswith('/'):
        return url + '/'
    return url

def fuzz_url(base_url, wordlist_file, max_threads=10):
    """Perform URL fuzzing with threading and better error handling."""
    results = []
    
    try:
        with open(wordlist_file, 'r', encoding='utf-8') as file:
            words = file.readlines()
    except Exception as e:
        logger.error(f"Error reading wordlist file: {str(e)}")
        return []
    
    base_url = ensure_trailing_slash(base_url)
    
    def check_url(word):
        word = word.strip()
        if not word:
            return None
            
        url = base_url + word
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=5, headers=headers, allow_redirects=False)
            return (url, response.status_code)
        except requests.RequestException:
            return (url, 'Error')
        except Exception as e:
            logger.error(f"Error checking {url}: {str(e)}")
            return (url, 'Error')
    
    # Use threading for better performance
    with threading.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(check_url, word) for word in words]
        for future in futures:
            result = future.result()
            if result:
                results.append(result)
    
    return results

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def index():
    """Handle URL checking and file upload with improved security."""
    results = None
    error = None
    download_link = False
    
    if request.method == 'POST':
        url = request.form.get('url')
        file = request.files.get('file')
        
        if url:
            url = url.strip()
            if not validate_url(url):
                error = 'Invalid URL format. Please enter a valid URL.'
            else:
                url = ensure_protocol(url)
                try:
                    results = check_url_status_and_get_title([url])
                except Exception as e:
                    logger.error(f"Error processing URL {url}: {str(e)}")
                    error = 'An error occurred while processing the URL.'
                    
        elif file and file.filename:
            if not allowed_file(file.filename):
                error = 'Invalid file type. Please upload a .txt or .csv file.'
            else:
                try:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    results = check_url_status_and_get_title(filepath)
                    download_link = True
                except Exception as e:
                    logger.error(f"Error processing file upload: {str(e)}")
                    error = 'An error occurred while processing the file.'
        else:
            error = 'Please provide either a URL or upload a file.'
    
    return render_template('index.html', results=results, error=error, download_link=download_link)

@app.route('/subdomain_finder', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def subdomain_finder():
    """Find subdomains for a given domain with improved functionality."""
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            domain = url.replace('http://', '').replace('https://', '').strip('/')
            if not domain:
                return render_template('subdomain_finder.html', error='Please enter a valid domain.')
            
            try:
                subdomains = fetch_subdomains(domain)
                if subdomains:
                    csv_filename = f'{domain}_subdomains_{int(time.time())}.csv'
                    csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
                    
                    with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerow(['Subdomain', 'Timestamp'])
                        for subdomain in subdomains:
                            csvwriter.writerow([subdomain, datetime.now().isoformat()])
                    
                    # Format subdomains into a table-friendly list
                    subdomains_in_rows = [subdomains[i:i+4] for i in range(0, len(subdomains), 4)]
                    return render_template('subdomain_finder.html', 
                                         subdomains=subdomains_in_rows, 
                                         csv_filename=csv_filename,
                                         total_count=len(subdomains))
                else:
                    return render_template('subdomain_finder.html', 
                                         error='No subdomains found for this domain.')
            except Exception as e:
                logger.error(f"Error in subdomain finder: {str(e)}")
                return render_template('subdomain_finder.html', 
                                     error='An error occurred while searching for subdomains.')
    
    return render_template('subdomain_finder.html')

@app.route('/fuzz', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def fuzz():
    """Perform URL fuzzing with improved security and performance."""
    if request.method == 'POST':
        base_url = request.form.get('url', '').strip()
        file = request.files.get('file')
        
        if not base_url or not validate_url(base_url):
            return render_template('fuzz.html', error='Please enter a valid base URL.')
        
        if not file or not file.filename:
            return render_template('fuzz.html', error='Please upload a wordlist file.')
        
        if not allowed_file(file.filename):
            return render_template('fuzz.html', error='Invalid file type. Please upload a .txt file.')
        
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            base_url = ensure_protocol(base_url)
            results = fuzz_url(base_url, filepath)
            
            if results:
                csv_filename = f'fuzz_results_{int(time.time())}.csv'
                csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
                
                with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['URL', 'Status Code', 'Timestamp'])
                    for url, status in results:
                        writer.writerow([url, status, datetime.now().isoformat()])
                
                return render_template('fuzz.html', results=results, csv_filename=csv_filename)
            else:
                return render_template('fuzz.html', error='No results found.')
                
        except Exception as e:
            logger.error(f"Error in fuzzing: {str(e)}")
            return render_template('fuzz.html', error='An error occurred during fuzzing.')

    return render_template('fuzz.html')

@app.route('/download/<filename>')
@limiter.limit("10 per minute")
def download_file(filename):
    """Serve files for download with security checks."""
    try:
        # Security check: ensure filename is safe
        if '..' in filename or filename.startswith('/'):
            return "Invalid filename", 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return "File not found", 404
        
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {str(e)}")
        return "Error downloading file", 500

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Rate limit exceeded. Please try again later."), 429

if __name__ == '__main__':
    # Ensure upload directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Set up logging
    logger.info("Starting SNIFFER application...")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
