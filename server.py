from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

API_KEY = "b2dd13cd3162e7ecc7eba6e9636fdd33fe8755b4"
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
