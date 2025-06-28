#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Email Intelligence Algorithm
Comprehensive demonstration of the email intelligence collection system
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

# Import our intelligence system
from email_intelligence_algorithm import EmailIntelligenceCollector, EmailIntelligence

def print_banner():
    """Print system banner"""
    print("=" * 80)
    print("🔍 EMAIL INTELLIGENCE COLLECTION SYSTEM")
    print("=" * 80)
    print("Comprehensive automated system for collecting and analyzing")
    print("information about email addresses using multiple sources.")
    print("=" * 80)
    print()

def print_step(step_num: int, title: str):
    """Print step header"""
    print(f"\n📋 STEP {step_num}: {title}")
    print("-" * 60)

def print_substep(title: str):
    """Print substep"""
    print(f"   🔸 {title}")

def print_result(emoji: str, title: str, content: str):
    """Print formatted result"""
    print(f"\n{emoji} {title}")
    if content:
        print(f"   {content}")

async def demo_algorithm():
    """Demonstrate the complete email intelligence algorithm"""
    
    print_banner()
    
    # Configuration
    target_email = "buch1202@mail.ru"
    
    print(f"🎯 TARGET EMAIL: {target_email}")
    print(f"⏰ START TIME: {datetime.now().isoformat()}")
    print()
    
    start_time = time.time()
    
    # Step 1: Initialize the collector
    print_step(1, "INITIALIZING EMAIL INTELLIGENCE COLLECTOR")
    
    async with EmailIntelligenceCollector() as collector:
        print_substep("✅ HTTP client session created")
        print_substep("✅ Search engines configured")
        print_substep("✅ PDF processing libraries loaded")
        print_substep("✅ Data extraction patterns loaded")
        
        # Step 2: Parse email
        print_step(2, "EMAIL PARSING AND VALIDATION")
        
        try:
            username, domain = collector.parse_email(target_email)
            print_result("✅", "Email parsed successfully", f"Username: {username}, Domain: {domain}")
        except ValueError as e:
            print_result("❌", "Email parsing failed", str(e))
            return
        
        # Step 3: Search general engines
        print_step(3, "SEARCHING GENERAL SEARCH ENGINES")
        
        print_substep("Searching Google...")
        print_substep("Searching Bing...")
        print_substep("Searching DuckDuckGo...")
        print_substep("Searching Yandex...")
        
        general_results = await collector.search_general_engines(target_email)
        
        found_engines = len([r for r in general_results.values() if r.get('mentions', 0) > 0])
        print_result("📊", "General search completed", 
                    f"Found mentions in {found_engines}/{len(general_results)} engines")
        
        # Step 4: Search PDF documents
        print_step(4, "SEARCHING PDF DOCUMENTS")
        
        print_substep("Searching Google Scholar...")
        print_substep("Searching for PDF files...")
        print_substep("Downloading and analyzing PDFs...")
        
        pdf_results = await collector.search_pdf_documents(target_email)
        
        if pdf_results:
            print_result("📄", "PDF documents found", f"{len(pdf_results)} documents analyzed")
            for i, pdf in enumerate(pdf_results[:3], 1):
                title = pdf.get('title', 'Unknown Title')
                if len(title) > 60:
                    title = title[:57] + "..."
                print(f"       {i}. {title}")
        else:
            print_result("📄", "PDF documents", "No documents found")
        
        # Step 5: Search document repositories
        print_step(5, "SEARCHING ACADEMIC REPOSITORIES")
        
        print_substep("Searching Academia.edu...")
        print_substep("Searching ResearchGate...")
        print_substep("Searching arXiv...")
        
        repo_results = await collector.search_document_repositories(target_email)
        
        academic_profiles = sum(len(r.get('profiles', [])) for r in repo_results.values())
        print_result("🎓", "Academic repositories", 
                    f"Found {academic_profiles} academic profiles")
        
        # Step 6: Search social platforms
        print_step(6, "SEARCHING SOCIAL MEDIA PLATFORMS")
        
        print_substep("Searching LinkedIn...")
        print_substep("Searching GitHub...")
        print_substep("Checking social media presence...")
        
        social_results = await collector.search_social_platforms(target_email, username)
        
        social_profiles = sum(len(r.get('profiles', [])) for r in social_results.values())
        print_result("📱", "Social media search", 
                    f"Found {social_profiles} social profiles")
        
        # Step 7: Initialize intelligence object
        print_step(7, "CREATING INTELLIGENCE PROFILE")
        
        intelligence = EmailIntelligence(
            email=target_email,
            timestamp=datetime.now().isoformat(),
            username=username,
            domain=domain
        )
        
        # Populate PDF documents
        intelligence.pdf_documents = pdf_results
        
        print_result("📋", "Intelligence profile created", 
                    f"Base profile initialized for {target_email}")
        
        # Step 8: Extract identity information
        print_step(8, "EXTRACTING IDENTITY INFORMATION")
        
        if pdf_results:
            print_substep("Analyzing PDF contexts...")
            collector.extract_identity_from_pdfs(intelligence, pdf_results)
            
            if intelligence.full_name:
                print_result("👤", "Identity extracted", intelligence.full_name)
            if intelligence.organization:
                print_result("🏢", "Organization identified", intelligence.organization)
            if intelligence.orcid_id:
                print_result("🆔", "ORCID found", intelligence.orcid_id)
        else:
            print_result("⚠️", "Identity extraction", "No PDF documents available for analysis")
        
        # Step 9: Calculate confidence score
        print_step(9, "CALCULATING CONFIDENCE SCORE")
        
        intelligence.confidence_score = collector.calculate_confidence_score(intelligence)
        
        confidence_level = "VERY LOW"
        if intelligence.confidence_score >= 0.8:
            confidence_level = "HIGH ✅"
        elif intelligence.confidence_score >= 0.6:
            confidence_level = "MEDIUM ⚠️"
        elif intelligence.confidence_score >= 0.3:
            confidence_level = "LOW 🔸"
        else:
            confidence_level = "VERY LOW ❌"
        
        print_result("🎯", "Confidence calculated", 
                    f"{intelligence.confidence_score:.2f}/1.0 ({confidence_level})")
        
        # Step 10: Add verification sources
        print_step(10, "IDENTIFYING VERIFICATION SOURCES")
        
        sources = []
        if general_results:
            sources.append("general_search")
        if pdf_results:
            sources.append("pdf_documents")
        if repo_results:
            sources.append("academic_repositories")
        if social_results:
            sources.append("social_media")
        
        intelligence.verification_sources = sources
        
        print_result("🔍", "Verification sources", ", ".join(sources))
        
        # Step 11: Generate reports
        print_step(11, "GENERATING REPORTS")
        
        # Create output directory
        output_dir = Path("/tmp/email_intelligence_demo")
        output_dir.mkdir(exist_ok=True)
        
        # Generate timestamp for files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_email = target_email.replace('@', '_at_').replace('.', '_')
        
        # Save JSON report
        json_path = output_dir / f"intelligence_{safe_email}_{timestamp}.json"
        collector.save_intelligence(intelligence, str(json_path))
        print_substep(f"JSON report saved: {json_path}")
        
        # Generate markdown report
        report = collector.generate_report(intelligence)
        md_path = output_dir / f"report_{safe_email}_{timestamp}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print_substep(f"Markdown report saved: {md_path}")
        
        # Step 12: Display final summary
        print_step(12, "FINAL INTELLIGENCE SUMMARY")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print()
        print("🎯 INTELLIGENCE SUMMARY")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📧 Email: {intelligence.email}")
        print(f"🎯 Confidence: {intelligence.confidence_score:.2f}/1.0 ({confidence_level})")
        print(f"⏰ Execution Time: {execution_time:.2f} seconds")
        print()
        
        # Identity Information
        if intelligence.full_name or intelligence.organization:
            print("👤 IDENTITY INFORMATION")
            if intelligence.full_name:
                print(f"   Name: {intelligence.full_name}")
            if intelligence.organization:
                print(f"   Organization: {intelligence.organization}")
            if intelligence.orcid_id:
                print(f"   ORCID: {intelligence.orcid_id}")
            print()
        
        # Evidence Summary
        print("📊 EVIDENCE SUMMARY")
        print(f"   PDF Documents: {len(intelligence.pdf_documents)}")
        print(f"   Alternative Emails: {len(intelligence.alternative_emails)}")
        print(f"   Phone Numbers: {len(intelligence.phone_numbers)}")
        print(f"   Academic Profiles: {len(intelligence.academic_profiles)}")
        print()
        
        # Technical Details
        print("🔧 TECHNICAL DETAILS")
        print(f"   Search Engines Queried: {len(general_results)}")
        print(f"   PDF Analysis: {'✅ Enabled' if pdf_results else '❌ No documents'}")
        print(f"   Repository Search: {'✅ Completed' if repo_results else '❌ No results'}")
        print(f"   Social Media Scan: {'✅ Completed' if social_results else '❌ No results'}")
        print()
        
        # Data Sources
        if intelligence.verification_sources:
            print("🔍 VERIFICATION SOURCES")
            for source in intelligence.verification_sources:
                print(f"   ✅ {source.replace('_', ' ').title()}")
            print()
        
        # Output Files
        print("📁 OUTPUT FILES")
        print(f"   📄 JSON: {json_path}")
        print(f"   📋 Report: {md_path}")
        print()
        
        print("=" * 80)
        print("🎉 EMAIL INTELLIGENCE COLLECTION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        return intelligence

def print_algorithm_overview():
    """Print overview of the algorithm components"""
    print("\n🔬 ALGORITHM OVERVIEW")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("📋 DATA COLLECTION PHASES:")
    print("   1. Email parsing and validation")
    print("   2. General search engine queries (Google, Bing, DuckDuckGo, Yandex)")
    print("   3. PDF document discovery and analysis")
    print("   4. Academic repository searches (Scholar, Academia, ResearchGate)")
    print("   5. Social media platform reconnaissance")
    print()
    print("🔍 EXTRACTION METHODS:")
    print("   • Regular expression patterns for names and organizations")
    print("   • PDF text extraction using multiple libraries")
    print("   • ORCID ID identification and verification")
    print("   • Contact information parsing")
    print("   • Academic profile discovery")
    print()
    print("📊 CONFIDENCE SCORING:")
    print("   • Basic email format validation (10%)")
    print("   • Full name identification (30%)")
    print("   • Organization verification (20%)")
    print("   • PDF document evidence (20%)")
    print("   • Academic credentials (ORCID) (10%)")
    print("   • Alternative contact methods (10%)")
    print()
    print("🛡️ SAFETY MEASURES:")
    print("   • Rate limiting between requests")
    print("   • Respect for robots.txt")
    print("   • Standard user agent headers")
    print("   • Public data only - no account breaching")
    print()

async def main():
    """Main demo function"""
    print_algorithm_overview()
    
    print("\n🚀 STARTING DEMONSTRATION...")
    print("Press Enter to begin the intelligence collection process...")
    input()
    
    try:
        intelligence = await demo_algorithm()
        
        print("\n❓ Would you like to see the detailed JSON output? (y/N): ", end="")
        show_json = input().lower().startswith('y')
        
        if show_json and intelligence:
            print("\n📄 DETAILED JSON OUTPUT:")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            from dataclasses import asdict
            print(json.dumps(asdict(intelligence), indent=2, ensure_ascii=False))
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
