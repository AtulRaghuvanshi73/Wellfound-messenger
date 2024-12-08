from flask import Flask, request, jsonify
from flask_cors import CORS
from wellfound_automation import WellfoundAutomation
import os
from dotenv import load_dotenv
import logging
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/set-cookies', methods=['POST'])
def set_cookies():
    try:
        cookies = request.json.get('cookies')
        if not cookies:
            return jsonify({'error': 'No cookies provided'}), 400
            
        # Store cookies in a file for later use
        with open('browser_cookies.json', 'w') as f:
            json.dump(cookies, f)
        
        return jsonify({'message': 'Cookies saved successfully'}), 200
    except Exception as e:
        logger.error(f"Error saving cookies: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_automation():
    automation = WellfoundAutomation(headless=True)
    
    try:
        # Use specific cookies for authentication
        if automation.setup_with_specific_cookies():
            logger.info("Successfully authenticated with specific cookies")
            return automation
        
        logger.error("Cookie authentication failed")
        raise Exception("Failed to authenticate with cookies")
    except Exception as e:
        automation.close()
        raise e

@app.route('/send', methods=['POST'])
def send_message():
    try:
        # Get data from request
        message_url = request.form.get('message_url') or request.json.get('message_url')
        message = request.form.get('message') or request.json.get('message')
        
        logger.info(f"Received request to send message to: {message_url}")
        
        if not message_url or not message:
            logger.error("Missing required fields")
            return jsonify({'error': 'Please provide both message URL and message'}), 400
            
        if not message_url.startswith('https://wellfound.com/'):
            logger.error("Invalid Wellfound URL")
            return jsonify({'error': 'Please provide a valid Wellfound URL'}), 400
        
        automation = None
        try:
            automation = get_automation()
            logger.info("Automation initialized successfully")
            
            # Check if it's a company message thread
            if '/jobs/messages/' in message_url:
                logger.info("Detected company message thread")
                success = automation.send_company_message(message_url, message)
            else:
                logger.info("Detected regular message")
                success = automation.send_message(message_url, message)
            
            if success:
                logger.info("Message sent successfully")
                return jsonify({'message': 'Message sent successfully!'}), 200
            else:
                logger.error("Failed to send message")
                return jsonify({'error': 'Failed to send message. Please check debug_screenshot.png for details.'}), 500
                
        except Exception as e:
            logger.error(f"Error during automation: {str(e)}", exc_info=True)
            error_msg = str(e)
            if "Authentication failed" in error_msg:
                return jsonify({'error': 'Authentication failed. Please check your cookies.'}), 401
            return jsonify({'error': f'Automation error: {error_msg}'}), 500
        finally:
            if automation:
                try:
                    automation.close()
                except Exception as e:
                    logger.error(f"Error closing automation: {str(e)}")
                    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
