#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Intelligence CLI
Command-line interface for email intelligence collection and analysis
"""

import argparse
import asyncio
import json
import sys
import yaml
from datetime import datetime
from pathlib import Path
from email_intelligence_algorithm import EmailIntelligenceCollector, EmailIntelligence

def load_config(config_path: str = "intelligence_config.yaml") -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"⚠️  Config file not found: {config_path}")
        print("Using default configuration...")
        return {}
    except yaml.YAMLError as e:
        print(f"❌ Error parsing config file: {e}")
        sys.exit(1)

def validate_email(email: str) -> bool:
    """Basic email validation"""
    return '@' in email and '.' in email.split('@')[1]

async def collect_single_email(email: str, config: dict, output_dir: str):
    """Collect intelligence for a single email"""
    if not validate_email(email):
        print(f"❌ Invalid email format: {email}")
        return
    
    print(f"🔍 Starting intelligence collection for: {email}")
    print("=" * 60)
    
    async with EmailIntelligenceCollector() as collector:
        # Collect intelligence
        intelligence = await collector.collect_intelligence(email)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_email = email.replace('@', '_at_').replace('.', '_')
        
        # Save JSON report
        json_path = output_path / f"intelligence_{safe_email}_{timestamp}.json"
        collector.save_intelligence(intelligence, str(json_path))
        
        # Generate and save markdown report
        report = collector.generate_report(intelligence)
        md_path = output_path / f"report_{safe_email}_{timestamp}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Print summary
        print_summary(intelligence)
        
        print(f"\n📁 Results saved to:")
        print(f"   📄 JSON: {json_path}")
        print(f"   📋 Report: {md_path}")
        
        return intelligence

def print_summary(intelligence: EmailIntelligence):
    """Print intelligence summary to console"""
    print(f"\n🎯 INTELLIGENCE SUMMARY")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📧 Email: {intelligence.email}")
    print(f"🎯 Confidence: {intelligence.confidence_score:.2f}/1.0", end="")
    
    if intelligence.confidence_score >= 0.8:
        print(" ✅ HIGH")
    elif intelligence.confidence_score >= 0.6:
        print(" ⚠️  MEDIUM") 
    elif intelligence.confidence_score >= 0.3:
        print(" 🔸 LOW")
    else:
        print(" ❌ VERY LOW")
    
    print(f"⏰ Analysis: {intelligence.timestamp}")
    print()
    
    # Identity Information
    if intelligence.full_name or intelligence.organization:
        print("👤 IDENTITY")
        if intelligence.full_name:
            print(f"   Name: {intelligence.full_name}")
        if intelligence.organization:
            print(f"   Org:  {intelligence.organization}")
        if intelligence.position:
            print(f"   Role: {intelligence.position}")
        if intelligence.location:
            print(f"   Loc:  {intelligence.location}")
        print()
    
    # Academic Information
    if intelligence.orcid_id or intelligence.academic_profiles:
        print("🎓 ACADEMIC")
        if intelligence.orcid_id:
            print(f"   ORCID: {intelligence.orcid_id}")
        if intelligence.academic_profiles:
            print(f"   Profiles: {len(intelligence.academic_profiles)}")
        print()
    
    # Document Evidence
    if intelligence.pdf_documents:
        print("📄 DOCUMENTS")
        for i, doc in enumerate(intelligence.pdf_documents[:3], 1):
            title = doc.get('title', 'Unknown Title')
            if len(title) > 50:
                title = title[:47] + "..."
            print(f"   {i}. {title}")
        if len(intelligence.pdf_documents) > 3:
            print(f"   ... and {len(intelligence.pdf_documents) - 3} more")
        print()
    
    # Contact Information
    if intelligence.alternative_emails or intelligence.phone_numbers:
        print("📞 CONTACT")
        if intelligence.alternative_emails:
            print(f"   Alt Emails: {len(intelligence.alternative_emails)}")
        if intelligence.phone_numbers:
            print(f"   Phones: {len(intelligence.phone_numbers)}")
        print()
    
    # Sources
    if intelligence.verification_sources:
        print("🔍 SOURCES")
        print(f"   {', '.join(intelligence.verification_sources)}")
        print()

async def collect_batch_emails(email_file: str, config: dict, output_dir: str):
    """Collect intelligence for emails from file"""
    try:
        with open(email_file, 'r') as f:
            emails = [line.strip() for line in f if line.strip() and validate_email(line.strip())]
    except FileNotFoundError:
        print(f"❌ Email file not found: {email_file}")
        return
    
    if not emails:
        print(f"❌ No valid emails found in: {email_file}")
        return
    
    print(f"📋 Processing {len(emails)} email(s) from: {email_file}")
    
    results = []
    for i, email in enumerate(emails, 1):
        print(f"\n[{i}/{len(emails)}] Processing: {email}")
        try:
            intelligence = await collect_single_email(email, config, output_dir)
            results.append(intelligence)
        except Exception as e:
            print(f"❌ Error processing {email}: {e}")
    
    # Generate batch summary
    print(f"\n📊 BATCH SUMMARY")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Total processed: {len(results)}")
    
    if results:
        high_conf = sum(1 for r in results if r.confidence_score >= 0.8)
        med_conf = sum(1 for r in results if 0.6 <= r.confidence_score < 0.8)
        low_conf = sum(1 for r in results if r.confidence_score < 0.6)
        
        print(f"High confidence: {high_conf}")
        print(f"Medium confidence: {med_conf}")
        print(f"Low confidence: {low_conf}")
        
        avg_confidence = sum(r.confidence_score for r in results) / len(results)
        print(f"Average confidence: {avg_confidence:.2f}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Email Intelligence Collection Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s buch1202@mail.ru                              # Single email analysis
  %(prog)s -f emails.txt                                 # Batch processing
  %(prog)s buch1202@mail.ru -o /custom/output/           # Custom output directory
  %(prog)s buch1202@mail.ru -c custom_config.yaml       # Custom config
  %(prog)s --test-config                                 # Test configuration
        """
    )
    
    # Main arguments
    parser.add_argument(
        'email',
        nargs='?',
        help='Email address to analyze'
    )
    
    parser.add_argument(
        '-f', '--file',
        metavar='FILE',
        help='File containing list of emails (one per line)'
    )
    
    parser.add_argument(
        '-o', '--output',
        metavar='DIR',
        default='/tmp/email_intelligence',
        help='Output directory (default: /tmp/email_intelligence)'
    )
    
    parser.add_argument(
        '-c', '--config',
        metavar='FILE',
        default='intelligence_config.yaml',
        help='Configuration file (default: intelligence_config.yaml)'
    )
    
    parser.add_argument(
        '--test-config',
        action='store_true',
        help='Test configuration and exit'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Email Intelligence Collector v1.0'
    )
    
    args = parser.parse_args()
    
    # Test configuration
    if args.test_config:
        print("🔧 Testing configuration...")
        config = load_config(args.config)
        print("✅ Configuration loaded successfully!")
        
        # Test PDF libraries
        try:
            import PyPDF2
            import pdfplumber
            print("✅ PDF processing libraries available")
        except ImportError as e:
            print(f"⚠️  PDF processing libraries missing: {e}")
        
        # Test async HTTP
        try:
            import aiohttp
            print("✅ HTTP client library available")
        except ImportError as e:
            print(f"❌ HTTP client library missing: {e}")
            sys.exit(1)
        
        print("🎉 All systems ready!")
        return
    
    # Validate arguments
    if not args.email and not args.file:
        parser.error("Must specify either email address or --file")
    
    if args.email and args.file:
        parser.error("Cannot specify both email and --file")
    
    # Load configuration
    config = load_config(args.config)
    
    # Run intelligence collection
    try:
        if args.file:
            asyncio.run(collect_batch_emails(args.file, config, args.output))
        else:
            asyncio.run(collect_single_email(args.email, config, args.output))
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
