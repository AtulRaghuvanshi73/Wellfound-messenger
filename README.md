# Wellfound Messenger

A web automation tool to send messages on Wellfound from a remote/server environment.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your Wellfound credentials in the `.env` file:
     ```
     WELLFOUND_EMAIL=your_email@example.com
     WELLFOUND_PASSWORD=your_password
     ```

3. Run the application:
```bash
python app.py
```

## Usage

1. Open your browser and navigate to `http://localhost:5000`
2. Enter the recipient's Wellfound profile URL (e.g., https://wellfound.com/u/username)
3. Type your message in the text box
4. Click "Send Message"

## Features

- Web interface for composing and sending messages
- Automated login using saved credentials
- Cookie persistence for maintaining sessions
- Headless browser operation for server environments
- Error handling and status feedback

## Security Notes

- Store your credentials securely in the `.env` file
- Never commit the `.env` file to version control
- The application uses secure cookie storage for sessions

## Requirements

- Python 3.8+
- Chrome/Chromium browser
- ChromeDriver (automatically managed)
