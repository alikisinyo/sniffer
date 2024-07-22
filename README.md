



![logo](https://github.com/user-attachments/assets/76eda83d-56cb-4997-ad1e-ba3692535349)

```markdown
# Flask Web Application

This Flask application provides functionalities for URL checking, subdomain finding, and URL fuzzing. It allows users to check the status and titles of URLs, find subdomains for a given domain, and perform URL fuzzing with a wordlist.

## Features

- **URL Checking**: Validate URLs and get their titles.
- **Subdomain Finder**: Find and export subdomains for a given domain.
- **URL Fuzzing**: Perform fuzz testing on URLs using a wordlist.

## Requirements

To run this application, you need to install the following dependencies:

- Flask
- Requests
- BeautifulSoup4

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/alikisinyo/sniffer.git
   cd 
   ```

2. **Create a virtual environment:**

   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Flask application:**

   ```bash
   python app.py
   ```

2. **Open your web browser and go to:**

   ```
   http://127.0.0.1:5000/
   ```

3. **Use the application:**

   - **URL Checking**: Enter a URL or upload a `.txt` file containing URLs to check their status and titles.
   - **Subdomain Finder**: Enter a domain to find its subdomains and download the results in CSV format.
   - **URL Fuzzing**: Enter a base URL and upload a `.txt` file containing a wordlist to perform URL fuzzing and download the results in CSV format.

## File Uploads

- The application allows you to upload `.txt` files containing URLs or wordlists for processing.

## Note

- Make sure the `uploads/` directory exists in the application root for file uploads. The application will create this directory if it does not exist.

## Acknowledgements

- This project uses [Flask](https://flask.palletsprojects.com/), [Requests](https://requests.readthedocs.io/), and [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) for web scraping and HTTP requests.

## Contact

For any questions or issues, please open an issue on the [GitHub repository](https://github.com/alikisinyo/sniffer/issues).
```
