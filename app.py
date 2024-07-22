from flask import Flask, request, render_template, send_from_directory
import os
import csv
import requests
import socket
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

def ensure_protocol(url):
    if not url.startswith(('http://', 'https://')):
        return 'http://' + url
    return url

def get_ip_and_location(url):
    try:
        ip_address = socket.gethostbyname(requests.utils.urlparse(url).hostname)
        ip_info = requests.get(f'http://ip-api.com/json/{ip_address}').json()
        lat = ip_info.get('lat', 'N/A')
        lon = ip_info.get('lon', 'N/A')
        location = f"{lat},{lon}"
        return ip_address, location
    except requests.RequestException:
        return 'N/A', 'N/A'

def check_url_status_and_get_title(urls):
    valid_urls_and_titles = []
    if isinstance(urls, list):  # Single URL case
        urls_list = urls
    else:  # File path case
        with open(urls, 'r') as infile:
            urls_list = infile.readlines()
    
    for url in urls_list:
        url = url.strip()
        if url:
            url = ensure_protocol(url)
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    title = soup.title.string if soup.title else 'No Title'
                    ip_address, location = get_ip_and_location(url)
                    valid_urls_and_titles.append((url, title, 'Success', ip_address, location))
                else:
                    valid_urls_and_titles.append((url, 'No Title', 'Failed', 'N/A', 'N/A'))
            except requests.RequestException:
                valid_urls_and_titles.append((url, 'No Title', 'Failed', 'N/A', 'N/A'))
    
    return valid_urls_and_titles

def fetch_subdomains(domain):
    domain = domain.replace('http://', '').replace('https://', '').strip('/')
    crt_sh_url = f'https://crt.sh/?q=%25.{domain}&output=json'
    try:
        response = requests.get(crt_sh_url)
        if response.status_code == 200:
            subdomains = set()
            for entry in response.json():
                name_value = entry['name_value']
                subdomains.update(name_value.split('\n'))
            return list(subdomains)
        else:
            return []
    except requests.RequestException:
        return []

def ensure_trailing_slash(url):
    if not url.endswith('/'):
        return url + '/'
    return url

def fuzz_url(base_url, wordlist_file):
    results = []
    with open(wordlist_file, 'r') as file:
        words = file.readlines()
    
    base_url = ensure_trailing_slash(base_url)

    for word in words:
        word = word.strip()
        if word:
            url = base_url + word
            try:
                response = requests.get(url)
                results.append((url, response.status_code))
            except requests.RequestException:
                results.append((url, 'Error'))

    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle URL checking and file upload."""
    results = None
    error = None
    download_link = False
    
    if request.method == 'POST':
        url = request.form.get('url')
        file = request.files.get('file')
        
        if url:
            url = ensure_protocol(url)
            try:
                results = check_url_status_and_get_title([url])
            except requests.RequestException as e:
                error = str(e)
                
        elif file and file.filename.endswith('.txt'):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            results = check_url_status_and_get_title(filename)
            download_link = True
        else:
            error = 'Invalid file type. Please upload a .txt file.'
    
    return render_template('index.html', results=results, error=error, download_link=download_link)

@app.route('/subdomain_finder', methods=['GET', 'POST'])
def subdomain_finder():
    """Find subdomains for a given domain."""
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            domain = url.replace('http://', '').replace('https://', '').strip('/')
            subdomains = fetch_subdomains(domain)
            if subdomains:
                csv_filename = f'{domain}_subdomains.csv'
                csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
                with open(csv_filepath, 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(['Subdomain'])
                    for subdomain in subdomains:
                        csvwriter.writerow([subdomain])
                # Format subdomains into a table-friendly list
                subdomains_in_rows = [subdomains[i:i+4] for i in range(0, len(subdomains), 4)]
                return render_template('subdomain_finder.html', subdomains=subdomains_in_rows, csv_filename=csv_filename)
    return render_template('subdomain_finder.html')

@app.route('/fuzz', methods=['GET', 'POST'])
def fuzz():
    """Perform URL fuzzing."""
    if request.method == 'POST':
        base_url = request.form['url']
        file = request.files['file']
        
        if file and file.filename.endswith('.txt'):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            base_url = ensure_protocol(base_url)  # Ensure URL has protocol
            results = fuzz_url(base_url, filename)
            
            csv_filename = 'fuzz_results.csv'
            with open(csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['URL', 'Status Code'])
                writer.writerows(results)

            return render_template('fuzz.html', results=results, csv_filename=csv_filename)

    return render_template('fuzz.html')

@app.route('/download/<filename>')
def download_file(filename):
    """Serve the requested file for download."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
