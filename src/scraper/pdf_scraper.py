"""
PDF Scraper for Verse by Verse Ministry
Scrapes Bible study PDFs from the website
"""
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Set
from tqdm import tqdm


class PDFScraper:
    """Scraper to download Bible study PDFs from Verse by Verse Ministry website"""
    
    def __init__(self, download_dir: str = "data/pdfs"):
        """
        Initialize the PDF scraper
        
        Args:
            download_dir: Directory to save downloaded PDFs
        """
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_page(self, url: str) -> Set[str]:
        """
        Scrape a page for PDF links
        
        Args:
            url: URL of the page to scrape
            
        Returns:
            Set of PDF URLs found on the page
        """
        pdf_urls = set()
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links on the page
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # Check if it's a PDF link
                if full_url.lower().endswith('.pdf'):
                    pdf_urls.add(full_url)
                    
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            
        return pdf_urls
    
    def download_pdf(self, url: str) -> str:
        """
        Download a PDF from a URL
        
        Args:
            url: URL of the PDF to download
            
        Returns:
            Path to the downloaded PDF file
        """
        try:
            # Extract filename from URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # Ensure filename ends with .pdf
            if not filename.lower().endswith('.pdf'):
                filename += '.pdf'
            
            filepath = os.path.join(self.download_dir, filename)
            
            # Skip if file already exists
            if os.path.exists(filepath):
                print(f"File already exists: {filename}")
                return filepath
            
            # Download the PDF
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            # Save to file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {filename}")
            return filepath
            
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return None
    
    def scrape_and_download(self, urls: List[str]) -> List[str]:
        """
        Scrape pages for PDFs and download them
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of paths to downloaded PDF files
        """
        all_pdf_urls = set()
        
        # Scrape all pages for PDF links
        print("Scraping pages for PDF links...")
        for url in urls:
            print(f"Scraping: {url}")
            pdf_urls = self.scrape_page(url)
            all_pdf_urls.update(pdf_urls)
            time.sleep(1)  # Be nice to the server
        
        print(f"\nFound {len(all_pdf_urls)} PDF files")
        
        # Download all PDFs
        print("\nDownloading PDFs...")
        downloaded_files = []
        for pdf_url in tqdm(all_pdf_urls):
            filepath = self.download_pdf(pdf_url)
            if filepath:
                downloaded_files.append(filepath)
            time.sleep(0.5)  # Be nice to the server
        
        print(f"\nSuccessfully downloaded {len(downloaded_files)} PDF files")
        return downloaded_files
