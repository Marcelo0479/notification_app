# Notification App

## Purpose
The purpose of this application is to automate the following tasks:

1. **Collect Data**: Gather information from official daily reports.
2. **Search for Updates**: Identify cases that include the term 'nomeio.'
3. **Extract Lawyer Names**: Retrieve the names of lawyers involved in these cases.
4. **Locate Phone Numbers**: Find the cell phone numbers of the lawyers on their respective autarky websites.
5. **Summarize Notifications**: Generate summaries of notifications using the GPT API.
6. **Send WhatsApp Messages**: Communicate with the lawyers by sending messages via WhatsApp.
7. **Monitor and Record Responses**: Keep track of and record the responses received.

To facilitate monitoring and response management, an HTML dashboard is available on the internet for real-time interaction and updates.

## Tools and Services Used
To develop this application, the following tools and services were utilized:

- **Docker**: Containerization platform.
- **Docker Compose**: Tool for defining and running multi-container Docker applications.
- **Flask**: Python web framework.
- **Python**: Programming language.
- **GPT API**: API for utilizing the GPT (Generative Pre-trained Transformer) language model.
- **2Captcha API**: Service for solving CAPTCHAs.
- **Green API**: (Please specify the exact service or library, as "Green API" is not a standard term.)

## Python Libraries
The following Python libraries were employed in the development of this application:

- **os**: Operating system-related functions.
- **re**: Regular expressions for pattern matching.
- **time**: Time-related functions.
- **datetime**: Date and time manipulation.
- **logging**: Logging framework.
- **requests**: HTTP requests library.
- **hashlib**: Cryptographic hash functions.
- **PyPDF2**: PDF processing library.
- **pathlib**: File and directory path manipulation.
- **pandas**: Data analysis and manipulation.
- **selenium**: Web automation and testing.
- **cv2**: OpenCV for image processing.
- **pytesseract**: OCR (Optical Character Recognition) tool.
- **twocaptcha**: Python client for the 2Captcha service.
- **flask**: Web framework for building web applications.
- **flask_socketio**: Extension for adding WebSocket support to Flask applications.
- **whatsapp_api_client_python**: Python client for WhatsApp API.

As a proof of concept (POC), CSV files were chosen to replace the traditional database.

