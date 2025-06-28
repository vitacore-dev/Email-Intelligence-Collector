#!/bin/bash

# PDF Search Script for email: buch1202@mail.ru
EMAIL="buch1202@mail.ru"
ENCODED_EMAIL="buch1202%40mail.ru"

echo "=== PDF Search for $EMAIL ==="
echo ""

# Search engines and specialized services
SEARCH_URLS=(
    "https://www.google.com/search?q=\"$ENCODED_EMAIL\"+filetype:pdf"
    "https://www.bing.com/search?q=\"$ENCODED_EMAIL\"+filetype:pdf"
    "https://duckduckgo.com/?q=\"$ENCODED_EMAIL\"+filetype:pdf"
    "https://yandex.ru/search/?text=$ENCODED_EMAIL%20filetype%3Apdf"
    "https://www.baidu.com/s?wd=$ENCODED_EMAIL%20filetype:pdf"
)

# Document repositories
DOC_REPOS=(
    "https://www.scribd.com/search?query=$ENCODED_EMAIL"
    "https://www.slideshare.net/search/slideshow?searchfrom=header&q=$EMAIL"
    "https://www.academia.edu/search?q=$EMAIL"
    "https://www.researchgate.net/search?q=$EMAIL"
    "https://arxiv.org/search/?query=$EMAIL&searchtype=all"
    "https://scholar.google.com/scholar?q=\"$EMAIL\""
)

# Function to search and extract PDF links
search_pdfs() {
    local url="$1"
    local service="$2"
    
    echo "Searching on $service..."
    
    # Get page content and look for PDF links
    pdf_links=$(curl -s -L "$url" \
        -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
        | grep -oiE 'href="[^"]*\.pdf[^"]*"' \
        | head -5)
    
    if [ -n "$pdf_links" ]; then
        echo "Found PDF links on $service:"
        echo "$pdf_links"
        echo ""
    else
        echo "No direct PDF links found on $service"
        
        # Look for any mentions of PDF or documents
        mentions=$(curl -s -L "$url" \
            -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
            | grep -i "pdf\|document" | head -2)
        
        if [ -n "$mentions" ]; then
            echo "Found document mentions on $service:"
            echo "$mentions" | sed 's/<[^>]*>//g' | sed 's/&[^;]*;//g'
        fi
        echo ""
    fi
}

# Search through search engines
echo "=== Searching through search engines ==="
for i in "${!SEARCH_URLS[@]}"; do
    case $i in
        0) search_pdfs "${SEARCH_URLS[$i]}" "Google" ;;
        1) search_pdfs "${SEARCH_URLS[$i]}" "Bing" ;;
        2) search_pdfs "${SEARCH_URLS[$i]}" "DuckDuckGo" ;;
        3) search_pdfs "${SEARCH_URLS[$i]}" "Yandex" ;;
        4) search_pdfs "${SEARCH_URLS[$i]}" "Baidu" ;;
    esac
    sleep 1  # Rate limiting
done

echo "=== Searching through document repositories ==="
for i in "${!DOC_REPOS[@]}"; do
    case $i in
        0) search_pdfs "${DOC_REPOS[$i]}" "Scribd" ;;
        1) search_pdfs "${DOC_REPOS[$i]}" "SlideShare" ;;
        2) search_pdfs "${DOC_REPOS[$i]}" "Academia.edu" ;;
        3) search_pdfs "${DOC_REPOS[$i]}" "ResearchGate" ;;
        4) search_pdfs "${DOC_REPOS[$i]}" "arXiv" ;;
        5) search_pdfs "${DOC_REPOS[$i]}" "Google Scholar" ;;
    esac
    sleep 1  # Rate limiting
done

echo "=== Search completed ==="
