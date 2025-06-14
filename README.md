# SNIFFER - Advanced Network Reconnaissance Tool

![SNIFFER Logo](static/images/logo.png)

A powerful Flask web application for network reconnaissance with a nostalgic Windows 95 interface. SNIFFER provides comprehensive tools for URL checking, subdomain discovery, and URL fuzzing with an authentic retro aesthetic.

## 🎮 Features

### Core Functionality
- **🔍 URL Status Checker**: Validate URLs and extract titles with IP geolocation
- **🌐 Subdomain Finder**: Discover subdomains using multiple sources (crt.sh, DNS enumeration)
- **🔧 URL Fuzzer**: Perform comprehensive fuzz testing with custom wordlists
- **📊 CSV Export**: Download results in organized CSV format
- **📁 File Upload Support**: Process multiple URLs from text files

### Enhanced Security & Performance
- **🛡️ Rate Limiting**: Built-in protection against abuse
- **🔒 Input Validation**: Secure URL and file handling
- **⚡ Multi-threading**: Fast processing with concurrent requests
- **📝 Comprehensive Logging**: Detailed activity tracking
- **🔄 Error Handling**: Robust error recovery and user feedback

### Windows 95 Theme
- **🎨 Authentic Retro UI**: Classic Windows 95 interface design
- **🖱️ Interactive Elements**: 3D buttons with proper outset/inset effects
- **📱 Responsive Design**: Works on all devices and screen sizes
- **🎯 User-Friendly**: Intuitive navigation and clear visual feedback

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/alikisinyo/sniffer.git
   cd sniffer
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser:**
   ```
   http://127.0.0.1:5000/
   ```

## 📖 Usage Guide

### URL Status Checker
- **Single URL**: Enter a URL to check its status, title, and IP location
- **Bulk Processing**: Upload a `.txt` file with multiple URLs (one per line)
- **Results**: View status codes, page titles, IP addresses, and geolocation data

### Subdomain Finder
- **Domain Input**: Enter a domain (e.g., `example.com`)
- **Multiple Sources**: Uses crt.sh certificates and DNS enumeration
- **Export**: Download results as CSV with timestamps

### URL Fuzzer
- **Base URL**: Enter the target URL (e.g., `https://example.com/`)
- **Wordlist**: Upload a `.txt` file with paths to test
- **Results**: Get status codes for each discovered endpoint

## 🛠️ Technical Details

### Dependencies
- **Flask**: Web framework
- **Requests**: HTTP library for API calls
- **BeautifulSoup4**: HTML parsing
- **Flask-Limiter**: Rate limiting
- **Flask-CORS**: Cross-origin support

### Architecture
- **Modular Design**: Clean separation of concerns
- **Error Handling**: Comprehensive exception management
- **Logging**: Detailed activity logs in `sniffer.log`
- **Security**: Input sanitization and validation
- **Performance**: Threading for concurrent operations

### File Structure
```
sniffer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── static/               # Static assets
│   ├── css/style.css     # Windows 95 theme styles
│   ├── js/script.js      # Interactive JavaScript
│   └── images/logo.png   # Application logo
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── subdomain_finder.html
│   ├── fuzz.html
│   ├── 404.html          # Error pages
│   └── 500.html
├── uploads/              # File upload directory
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key (default: auto-generated)
- `UPLOAD_FOLDER`: Upload directory path (default: `uploads/`)
- `MAX_CONTENT_LENGTH`: Max file size in bytes (default: 16MB)

### Rate Limits
- **Home Page**: 10 requests per minute
- **Subdomain Finder**: 5 requests per minute
- **URL Fuzzer**: 3 requests per minute
- **File Downloads**: 10 requests per minute

## 📝 API Endpoints

- `GET /`: Main application interface
- `POST /`: URL checking and file processing
- `GET /subdomain_finder`: Subdomain discovery tool
- `POST /subdomain_finder`: Subdomain search
- `GET /fuzz`: URL fuzzing interface
- `POST /fuzz`: Fuzz testing execution
- `GET /download/<filename>`: File download
- `GET /api/health`: Health check endpoint

## 🎨 Windows 95 Theme Features

### Visual Design
- **Authentic Colors**: Classic Windows 95 color palette
- **3D Effects**: Proper outset/inset borders and shadows
- **Typography**: MS Sans Serif font family
- **Interactive Elements**: Hover effects and click animations

### User Experience
- **Responsive Layout**: Works on desktop and mobile
- **Intuitive Navigation**: Clear menu structure
- **Visual Feedback**: Loading states and error handling
- **Accessibility**: Proper contrast and readable text

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Flask Community**: For the excellent web framework
- **Windows 95**: For the nostalgic inspiration
- **Open Source Tools**: BeautifulSoup4, Requests, and other libraries
- **GitHub**: For hosting and collaboration tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/alikisinyo/sniffer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/alikisinyo/sniffer/discussions)
- **Email**: Open an issue for contact information

---

**Made with ❤️ and nostalgia for the golden age of computing**
