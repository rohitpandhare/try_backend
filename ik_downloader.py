import requests
import json
import logging
import os
import re
import datetime
import argparse
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API_TOKEN = "63ec6326ae3d158b05d38d232f2a063e1cc79bcb"
API_TOKEN = os.getenv("API_KEY")  # Fetch the API key from Vercel's environment variables

if not API_TOKEN:
    raise ValueError("API Key not found! Make sure to set the API_KEY environment variable in your Vercel project settings.")
    
class IndianKanoonDownloader:
    def __init__(self):
        self.api_key = API_TOKEN
        self.base_url = "https://api.indiankanoon.org"
        self.headers = {
            'Authorization': f"Token {self.api_key}",
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
    def search_documents(self, query: str, pagenum: int = 0) -> Dict[str, Any]:
        """
        Search documents using the Indian Kanoon API
        
        Args:
            query (str): Search query string
            pagenum (int): Page number for pagination
            
        Returns:
            dict: JSON response from the API
        """
        try:
            url = f"{self.base_url}/search/"
            payload = {
                'formInput': query,
                'pagenum': pagenum
            }
            
            logger.info(f"Searching for: {query} (page {pagenum})")
            response = requests.post(url, data=payload, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Search request failed: {str(e)}")
            raise

    def get_document(self, docid: str) -> Dict[str, Any]:
        """
        Fetch a specific document using its ID
        
        Args:
            docid (str): Document ID
            
        Returns:
            dict: JSON response containing the document
        """
        try:
            url = f"{self.base_url}/doc/{docid}/"
            
            logger.info(f"Fetching document: {docid}")
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Document fetch failed: {str(e)}")
            raise

    def save_document(self, doc_data: Dict[str, Any], output_dir: str) -> str:
        """
        Save document data to a file
        
        Args:
            doc_data (dict): Document data to save
            output_dir (str): Directory to save the file
            
        Returns:
            str: Path to the saved file
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Create filename from title or document ID
            title = doc_data.get('title', 'untitled')
            docid = doc_data.get('tid', 'unknown')
            
            # Sanitize filename
            safe_title = re.sub(r'[^\w\-]', '_', title)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_title}_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            # Save document data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(doc_data, f, indent=4, ensure_ascii=False)
                
            logger.info(f"Saved document to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save document: {str(e)}")
            raise

    def download_search_results(self, query: str, num_pages: int = 1, output_dir: str = "downloads") -> None:
        """
        Download multiple pages of search results and their documents
        
        Args:
            query (str): Search query
            num_pages (int): Number of pages to download
            output_dir (str): Directory to save the documents
        """
        try:
            total_docs = 0
            
            for page in range(num_pages):
                logger.info(f"Fetching page {page + 1} of {num_pages}")
                
                # Get search results
                results = self.search_documents(query, page)
                docs = results.get('docs', [])
                
                if not docs:
                    logger.info(f"No more results found after page {page + 1}")
                    break
                
                # Download each document
                for doc in docs:
                    docid = doc.get('tid')
                    if docid:
                        try:
                            # Get full document
                            full_doc = self.get_document(docid)
                            # Save document
                            self.save_document(full_doc, output_dir)
                            total_docs += 1
                        except Exception as e:
                            logger.warning(f"Failed to download document {docid}: {str(e)}")
                            continue
                
            logger.info(f"Successfully downloaded {total_docs} documents")
            
        except Exception as e:
            logger.error(f"Download process failed: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Download documents from Indian Kanoon')
    parser.add_argument('-q', '--query', type=str, required=True,
                      help='Search query string')
    parser.add_argument('-p', '--pages', type=int, default=1,
                      help='Number of pages to download (default: 1)')
    parser.add_argument('-o', '--output', type=str, default='downloads',
                      help='Output directory for downloaded documents (default: downloads)')
    
    args = parser.parse_args()
    
    try:
        downloader = IndianKanoonDownloader()
        downloader.download_search_results(args.query, args.pages, args.output)
        
    except Exception as e:
        logger.error(f"Program failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
