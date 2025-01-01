from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import requests
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

API_TOKEN = "63ec6326ae3d158b05d38d232f2a063e1cc79bcb"
# API_TOKEN = os.getenv("API_KEY")  # Fetch the API key from Vercel's environment variables
# if not API_TOKEN:
#     raise ValueError("API Key not found! Make sure to set the API_KEY environment variable in your Vercel project settings.")
    
API_KEY = API_TOKEN
BASE_URL = "https://api.indiankanoon.org"

def get_headers():
    return {
        'Authorization': f"Token {API_KEY}",
        'Content-Type': 'application/x-www-form-urlencoded'
    }

@app.route('/search/', methods=['POST'])
def search():
    try:
        data = request.get_json()
        query = data.get('formInput')
        pagenum = data.get('pagenum', 0)

        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400

        url = f"{BASE_URL}/search/"
        payload = {
            'formInput': query,
            'pagenum': pagenum
        }

        response = requests.post(url, data=payload, headers=get_headers())
        response.raise_for_status()
        return jsonify(response.json())

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/doc/<docid>/', methods=['POST'])
def get_document(docid):
    try:
        url = f"{BASE_URL}/doc/{docid}/"
        response = requests.post(url, headers=get_headers())
        response.raise_for_status()
        return jsonify(response.json())

    except Exception as e:
        logger.error(f"Document fetch error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
