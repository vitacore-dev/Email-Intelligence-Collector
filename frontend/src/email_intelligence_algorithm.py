#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Intelligence Collection Algorithm
Comprehensive system for gathering and analyzing information about email addresses
"""

import asyncio
import aiohttp
import json
import re
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from urllib.parse import quote, urljoin
import hashlib
import time

# PDF processing
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/email_intelligence.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EmailIntelligence:
    """Data structure for email intelligence"""
    email: str
    timestamp: str
    
    # Basic info
    domain: str = ""
    username: str = ""
    
    # Identity information
    full_name: str = ""
    first_name: str = ""
    last_name: str = ""
    display_name: str = ""
    
    # Professional information
    organization: str = ""
    position: str = ""
    department: str = ""
    location: str = ""
    
    # Contact information
    phone_numbers: List[str] = None
    alternative_emails: List[str] = None
    social_profiles: List[Dict[str, str]] = None
    
    # Online presence
    websites: List[str] = None
    social_media: List[Dict[str, str]] = None
    academic_profiles: List[Dict[str, str]] = None
    
    # Document findings
    pdf_documents: List[Dict[str, Any]] = None
    publications: List[Dict[str, str]] = None
    
    # Technical details
    orcid_id: str = ""
    linkedin_profile: str = ""
    github_profile: str = ""
    
    # Verification
    confidence_score: float = 0.0
    verification_sources: List[str] = None
    
    def __post_init__(self):
        if self.phone_numbers is None:
            self.phone_numbers = []
        if self.alternative_emails is None:
            self.alternative_emails = []
        if self.social_profiles is None:
            self.social_profiles = []
        if self.websites is None:
            self.websites = []
        if self.social_media is None:
            self.social_media = []
        if self.academic_profiles is None:
            self.academic_profiles = []
        if self.pdf_documents is None:
            self.pdf_documents = []
        if self.publications is None:
            self.publications = []
        if self.verification_sources is None:
            self.verification_sources = []

class EmailIntelligenceCollector:
    """Main class for email intelligence collection"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        
        # Search engines and services
        self.search_engines = [
            "https://www.google.com/search?q=\"{email}\"",
            "https://www.bing.com/search?q=\"{email}\"",
            "https://duckduckgo.com/?q=\"{email}\"",
            "https://yandex.ru/search/?text={email}",
            "https://www.baidu.com/s?wd={email}",
        ]
        
        self.pdf_search_engines = [
            "https://www.google.com/search?q=\"{email}\"+filetype:pdf",
            "https://www.bing.com/search?q=\"{email}\"+filetype:pdf",
            "https://duckduckgo.com/?q=\"{email}\"+filetype:pdf",
            "https://scholar.google.com/scholar?q=\"{email}\"",
        ]
        
        self.document_repositories = [
            "https://www.scribd.com/search?query={email}",
            "https://www.slideshare.net/search/slideshow?searchfrom=header&q={email}",
            "https://www.academia.edu/search?q={email}",
            "https://www.researchgate.net/search?q={email}",
            "https://arxiv.org/search/?query={email}&searchtype=all",
        ]
        
        self.social_platforms = [
            "https://www.linkedin.com/search/results/people/?keywords={email}",
            "https://github.com/search?q={email}&type=users",
            "https://twitter.com/search?q={email}",
            "https://www.facebook.com/search/people/?q={email}",
            "https://www.instagram.com/{username}/",
        ]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def parse_email(self, email: str) -> tuple:
        """Parse email into username and domain"""
        try:
            username, domain = email.split('@')
            return username, domain
        except ValueError:
            raise ValueError(f"Invalid email format: {email}")

    async def fetch_url(self, url: str, timeout: int = 30) -> Optional[str]:
        """Fetch URL content with error handling"""
        try:
            async with self.session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    async def search_general_engines(self, email: str) -> Dict[str, Any]:
        """Search general search engines for email mentions"""
        results = {}
        
        for engine_url in self.search_engines:
            engine_name = engine_url.split('//')[1].split('/')[0].split('.')[1]
            url = engine_url.format(email=quote(email))
            
            logger.info(f"Searching {engine_name} for {email}")
            content = await self.fetch_url(url)
            
            if content:
                results[engine_name] = {
                    'url': url,
                    'content_length': len(content),
                    'mentions': content.lower().count(email.lower()),
                    'social_links': self.extract_social_links(content),
                    'contact_info': self.extract_contact_info(content),
                }
            
            # Rate limiting
            await asyncio.sleep(1)
        
        return results

    async def search_pdf_documents(self, email: str) -> List[Dict[str, Any]]:
        """Search for PDF documents containing the email"""
        pdf_results = []
        
        for engine_url in self.pdf_search_engines:
            engine_name = engine_url.split('//')[1].split('/')[0].split('.')[1]
            url = engine_url.format(email=quote(email))
            
            logger.info(f"Searching {engine_name} for PDF documents with {email}")
            content = await self.fetch_url(url)
            
            if content:
                pdf_links = self.extract_pdf_links(content)
                for pdf_link in pdf_links:
                    pdf_info = await self.analyze_pdf_document(pdf_link, email)
                    if pdf_info:
                        pdf_info['source'] = engine_name
                        pdf_results.append(pdf_info)
            
            await asyncio.sleep(1)
        
        return pdf_results

    async def search_document_repositories(self, email: str) -> Dict[str, Any]:
        """Search academic and document repositories"""
        results = {}
        
        for repo_url in self.document_repositories:
            repo_name = repo_url.split('//')[1].split('/')[0].split('.')[1]
            url = repo_url.format(email=quote(email))
            
            logger.info(f"Searching {repo_name} for {email}")
            content = await self.fetch_url(url)
            
            if content:
                results[repo_name] = {
                    'url': url,
                    'profiles': self.extract_academic_profiles(content),
                    'publications': self.extract_publications(content),
                }
            
            await asyncio.sleep(1)
        
        return results

    async def search_social_platforms(self, email: str, username: str) -> Dict[str, Any]:
        """Search social media platforms"""
        results = {}
        
        for platform_url in self.social_platforms:
            platform_name = platform_url.split('//')[1].split('/')[0].split('.')[1]
            
            # Use email for most platforms, username for some
            search_term = username if 'instagram' in platform_url else email
            url = platform_url.format(email=quote(email), username=username)
            
            logger.info(f"Searching {platform_name} for {search_term}")
            content = await self.fetch_url(url)
            
            if content:
                results[platform_name] = {
                    'url': url,
                    'profiles': self.extract_social_profiles(content, platform_name),
                }
            
            await asyncio.sleep(1)
        
        return results

    def extract_pdf_links(self, content: str) -> List[str]:
        """Extract PDF links from search results"""
        pdf_pattern = r'href="([^"]*\.pdf[^"]*)"'
        links = re.findall(pdf_pattern, content, re.IGNORECASE)
        
        # Clean and validate links
        clean_links = []
        for link in links:
            if not link.startswith('http'):
                continue
            clean_links.append(link)
        
        return clean_links[:5]  # Limit to first 5 PDFs

    async def analyze_pdf_document(self, pdf_url: str, target_email: str) -> Optional[Dict[str, Any]]:
        """Download and analyze PDF document"""
        if not PDF_AVAILABLE:
            logger.warning("PDF processing libraries not available")
            return None
        
        try:
            # Download PDF
            pdf_content = await self.fetch_url(pdf_url)
            if not pdf_content:
                return None
            
            # Save temporarily
            temp_path = f"/tmp/pdf_{hashlib.md5(pdf_url.encode()).hexdigest()}.pdf"
            with open(temp_path, 'wb') as f:
                async with self.session.get(pdf_url) as response:
                    f.write(await response.read())
            
            # Extract text
            text = self.extract_pdf_text(temp_path)
            
            # Analyze content
            email_contexts = self.find_email_contexts(text, target_email)
            authors = self.extract_authors(text)
            institutions = self.extract_institutions(text)
            
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
            
            if email_contexts:
                return {
                    'url': pdf_url,
                    'title': self.extract_pdf_title(text),
                    'authors': authors,
                    'institutions': institutions,
                    'email_contexts': email_contexts,
                    'text_length': len(text),
                }
        
        except Exception as e:
            logger.error(f"Error analyzing PDF {pdf_url}: {e}")
        
        return None

    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF using multiple methods"""
        text = ""
        
        try:
            # Try pdfplumber first (more accurate)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                logger.error(f"PyPDF2 also failed: {e}")
        
        return text

    def find_email_contexts(self, text: str, target_email: str) -> List[Dict[str, str]]:
        """Find contexts where email appears in text"""
        lines = text.split('\n')
        contexts = []
        
        for i, line in enumerate(lines):
            if target_email.lower() in line.lower():
                start = max(0, i-2)
                end = min(len(lines), i+3)
                
                contexts.append({
                    'line_number': i+1,
                    'line': line.strip(),
                    'context': '\n'.join(lines[start:end]),
                })
        
        return contexts

    def extract_authors(self, text: str) -> List[str]:
        """Extract author names from text"""
        patterns = [
            r'[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.?\s*[А-ЯЁ]\.?\s*[А-ЯЁ][а-яё]+',  # Russian names
            r'[A-Z][a-z]+\s+[A-Z]\.?\s*[A-Z]\.?\s*[A-Z][a-z]+',  # English names
            r'[А-ЯЁ]\.?\s*[А-ЯЁ]\.?\s*[А-ЯЁ][а-яё]+',  # Initials + surname
        ]
        
        authors = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            authors.extend(matches)
        
        return list(set(authors))

    def extract_institutions(self, text: str) -> List[str]:
        """Extract institution names from text"""
        patterns = [
            r'[А-ЯЁ][а-яё]*\s+[а-яё]*\s*[Уу]ниверситет',
            r'[А-ЯЁ][а-яё]*\s+[а-яё]*\s*[Ии]нститут',
            r'[А-ЯЁ][а-яё]*\s+[а-яё]*\s*[Цц]ентр',
            r'[А-ЯЁ][а-яё]*\s+[а-яё]*\s*[Аа]кадеми[яи]',
        ]
        
        institutions = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            institutions.extend(matches)
        
        return list(set(institutions))

    def extract_pdf_title(self, text: str) -> str:
        """Extract title from PDF text"""
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if len(line.strip()) > 10 and len(line.strip()) < 200:
                return line.strip()
        return "Unknown Title"

    def extract_social_links(self, content: str) -> List[str]:
        """Extract social media links from content"""
        social_patterns = [
            r'https?://(?:www\.)?linkedin\.com/in/[^"\s]+',
            r'https?://(?:www\.)?github\.com/[^"\s]+',
            r'https?://(?:www\.)?twitter\.com/[^"\s]+',
            r'https?://(?:www\.)?facebook\.com/[^"\s]+',
            r'https?://(?:www\.)?instagram\.com/[^"\s]+',
        ]
        
        links = []
        for pattern in social_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            links.extend(matches)
        
        return list(set(links))

    def extract_contact_info(self, content: str) -> Dict[str, List[str]]:
        """Extract contact information from content"""
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Phone patterns
        phone_patterns = [
            r'\+\d{1,3}\s*\(\d{3}\)\s*\d{3}-\d{2}-\d{2}',
            r'\+\d{1,3}\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}',
            r'\(\d{3}\)\s*\d{3}-\d{4}',
        ]
        
        emails = re.findall(email_pattern, content)
        phones = []
        
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, content))
        
        return {
            'emails': list(set(emails)),
            'phones': list(set(phones))
        }

    def extract_academic_profiles(self, content: str) -> List[Dict[str, str]]:
        """Extract academic profile information"""
        # ORCID pattern
        orcid_pattern = r'orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])'
        orcids = re.findall(orcid_pattern, content, re.IGNORECASE)
        
        profiles = []
        for orcid in orcids:
            profiles.append({
                'type': 'ORCID',
                'id': orcid,
                'url': f'https://orcid.org/{orcid}'
            })
        
        return profiles

    def extract_publications(self, content: str) -> List[Dict[str, str]]:
        """Extract publication information"""
        # Simple publication title extraction
        # This would need more sophisticated logic for real-world use
        return []

    def extract_social_profiles(self, content: str, platform: str) -> List[Dict[str, str]]:
        """Extract social media profile information"""
        profiles = []
        
        if platform == 'linkedin':
            # LinkedIn profile extraction logic
            pass
        elif platform == 'github':
            # GitHub profile extraction logic
            pass
        
        return profiles

    def calculate_confidence_score(self, intelligence: EmailIntelligence) -> float:
        """Calculate confidence score based on collected data"""
        score = 0.0
        
        # Basic email verification
        if intelligence.email and '@' in intelligence.email:
            score += 0.1
        
        # Identity information
        if intelligence.full_name:
            score += 0.3
        
        # Professional information
        if intelligence.organization:
            score += 0.2
        
        # Contact verification
        if intelligence.alternative_emails:
            score += 0.1
        
        # Document evidence
        if intelligence.pdf_documents:
            score += 0.2
        
        # Academic verification
        if intelligence.orcid_id:
            score += 0.1
        
        return min(score, 1.0)

    async def collect_intelligence(self, email: str) -> EmailIntelligence:
        """Main method to collect all intelligence about an email"""
        logger.info(f"Starting intelligence collection for {email}")
        start_time = time.time()
        
        # Parse email
        username, domain = self.parse_email(email)
        
        # Initialize intelligence object
        intelligence = EmailIntelligence(
            email=email,
            timestamp=datetime.now().isoformat(),
            username=username,
            domain=domain
        )
        
        try:
            # Collect data from various sources
            logger.info("Searching general search engines...")
            general_results = await self.search_general_engines(email)
            
            logger.info("Searching for PDF documents...")
            pdf_results = await self.search_pdf_documents(email)
            intelligence.pdf_documents = pdf_results
            
            logger.info("Searching document repositories...")
            repo_results = await self.search_document_repositories(email)
            
            logger.info("Searching social platforms...")
            social_results = await self.search_social_platforms(email, username)
            
            # Extract identity information from PDF results
            if pdf_results:
                self.extract_identity_from_pdfs(intelligence, pdf_results)
            
            # Calculate confidence score
            intelligence.confidence_score = self.calculate_confidence_score(intelligence)
            
            # Add verification sources
            intelligence.verification_sources = [
                source for source in ['general_search', 'pdf_documents', 'repositories', 'social_media']
                if any([general_results, pdf_results, repo_results, social_results])
            ]
            
            logger.info(f"Intelligence collection completed in {time.time() - start_time:.2f}s")
            logger.info(f"Confidence score: {intelligence.confidence_score:.2f}")
            
        except Exception as e:
            logger.error(f"Error during intelligence collection: {e}")
        
        return intelligence

    def extract_identity_from_pdfs(self, intelligence: EmailIntelligence, pdf_results: List[Dict[str, Any]]):
        """Extract identity information from PDF analysis results"""
        for pdf in pdf_results:
            if pdf.get('email_contexts'):
                for context in pdf['email_contexts']:
                    # Try to extract name from context
                    name_match = self.extract_name_from_context(context['context'])
                    if name_match and not intelligence.full_name:
                        intelligence.full_name = name_match
                    
                    # Extract ORCID if present
                    orcid_match = re.search(r'ORCID[:-]?\s*(\d{4}-\d{4}-\d{4}-\d{3}[\dX])', context['context'])
                    if orcid_match and not intelligence.orcid_id:
                        intelligence.orcid_id = orcid_match.group(1)
            
            # Extract organization from institutions
            if pdf.get('institutions') and not intelligence.organization:
                intelligence.organization = pdf['institutions'][0] if pdf['institutions'] else ""

    def extract_name_from_context(self, context: str) -> Optional[str]:
        """Extract person name from context"""
        # Look for patterns like "Name Surname, position, organization"
        patterns = [
            r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.?\s*[А-ЯЁ]\.?\s*[А-ЯЁ][а-яё]+)',  # Russian
            r'([A-Z][a-z]+\s+[A-Z]\.?\s*[A-Z]\.?\s*[A-Z][a-z]+)',  # English
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context)
            if match:
                return match.group(1)
        
        return None

    def save_intelligence(self, intelligence: EmailIntelligence, output_path: str):
        """Save intelligence to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(intelligence), f, ensure_ascii=False, indent=2)
        
        logger.info(f"Intelligence saved to {output_path}")

    def generate_report(self, intelligence: EmailIntelligence) -> str:
        """Generate human-readable report"""
        report = f"""
# Email Intelligence Report

## Target Email: {intelligence.email}
**Analysis Date:** {intelligence.timestamp}
**Confidence Score:** {intelligence.confidence_score:.2f}/1.0

## Identity Information
- **Full Name:** {intelligence.full_name or 'Not found'}
- **Organization:** {intelligence.organization or 'Not found'}
- **Position:** {intelligence.position or 'Not found'}
- **Location:** {intelligence.location or 'Not found'}

## Academic Information
- **ORCID ID:** {intelligence.orcid_id or 'Not found'}
- **Publications Found:** {len(intelligence.publications)}

## Contact Information
- **Alternative Emails:** {len(intelligence.alternative_emails)}
- **Phone Numbers:** {len(intelligence.phone_numbers)}

## Document Evidence
- **PDF Documents:** {len(intelligence.pdf_documents)}
- **Academic Profiles:** {len(intelligence.academic_profiles)}

## Social Media Presence
- **Social Profiles:** {len(intelligence.social_media)}
- **Websites:** {len(intelligence.websites)}

## Verification Sources
{', '.join(intelligence.verification_sources) if intelligence.verification_sources else 'None'}

"""
        
        if intelligence.pdf_documents:
            report += "\n## PDF Document Details\n"
            for i, pdf in enumerate(intelligence.pdf_documents, 1):
                report += f"""
### Document {i}
- **URL:** {pdf.get('url', 'Unknown')}
- **Title:** {pdf.get('title', 'Unknown')}
- **Authors:** {', '.join(pdf.get('authors', []))}
- **Institutions:** {', '.join(pdf.get('institutions', []))}
"""

        return report

async def main():
    """Example usage of the Email Intelligence Collector"""
    email = "buch1202@mail.ru"
    
    async with EmailIntelligenceCollector() as collector:
        # Collect intelligence
        intelligence = await collector.collect_intelligence(email)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"/tmp/intelligence_{email.replace('@', '_at_')}_{timestamp}.json"
        collector.save_intelligence(intelligence, output_path)
        
        # Generate report
        report = collector.generate_report(intelligence)
        report_path = f"/tmp/report_{email.replace('@', '_at_')}_{timestamp}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\nDetailed results saved to:")
        print(f"- JSON: {output_path}")
        print(f"- Report: {report_path}")

if __name__ == "__main__":
    asyncio.run(main())
