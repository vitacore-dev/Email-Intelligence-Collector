#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Email Intelligence Collection System
Comprehensive system for gathering and analyzing information about email addresses
Integrates all previously developed components into a unified, reproducible algorithm
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Internal modules
from .data_collector import DataCollector
from .academic_intelligence import AcademicIntelligenceCollector
from .digital_twin import DigitalTwinCreator
from .social_collectors import BaseCollector, GoogleSearchCollector
from .search_engines import SearchEngineManager
from .web_scraper import WebScraper
from .email_validator import EmailValidator

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class IntelligenceResults:
    """Comprehensive intelligence results structure"""
    email: str
    analysis_timestamp: str
    processing_time: float
    
    # Basic validation
    email_validation: Dict[str, Any]
    
    # Core data collection
    general_intelligence: Dict[str, Any]
    search_results: List[Dict[str, Any]]
    social_profiles: List[Dict[str, Any]]
    
    # Academic analysis
    academic_profile: Dict[str, Any]
    academic_publications: List[Dict[str, Any]]
    academic_confidence: Dict[str, float]
    
    # Digital identity
    digital_twin: Dict[str, Any]
    personality_analysis: Dict[str, Any]
    network_analysis: Dict[str, Any]
    
    # Verification and scoring
    overall_confidence_score: float
    data_completeness_score: float
    verification_sources: List[str]
    
    # Analysis summary
    key_findings: List[str]
    recommendations: List[str]
    risk_indicators: List[str]

class AutomatedIntelligenceSystem:
    """
    Automated Email Intelligence Collection System
    
    This system integrates all email intelligence gathering capabilities
    into a single, comprehensive, reproducible workflow.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.start_time = None
        self.results = None
        
        # Configure analysis parameters
        self.max_processing_time = self.config.get('max_processing_time', 300)  # 5 minutes
        self.enable_deep_search = self.config.get('enable_deep_search', True)
        self.enable_academic_analysis = self.config.get('enable_academic_analysis', True)
        self.enable_social_analysis = self.config.get('enable_social_analysis', True)
        self.enable_digital_twin = self.config.get('enable_digital_twin', True)
        
        # Rate limiting
        self.request_delay = self.config.get('request_delay', 1.0)
        self.max_concurrent_requests = self.config.get('max_concurrent_requests', 3)
        
        logger.info("Automated Intelligence System initialized")

    async def analyze_email(self, email: str) -> IntelligenceResults:
        """
        Main method to perform comprehensive email intelligence analysis
        
        Args:
            email: Target email address for analysis
            
        Returns:
            IntelligenceResults: Comprehensive analysis results
        """
        self.start_time = time.time()
        logger.info(f"Starting comprehensive analysis for {email}")
        
        try:
            # Phase 1: Email validation and basic checks
            logger.info("Phase 1: Email validation")
            email_validation = await self._validate_email(email)
            
            if not email_validation.get('is_valid', False):
                logger.warning(f"Email {email} failed validation")
                return self._create_minimal_results(email, email_validation)
            
            # Phase 2: General data collection
            logger.info("Phase 2: General data collection")
            general_data = await self._collect_general_data(email)
            
            # Phase 3: Search engine analysis
            logger.info("Phase 3: Search engine analysis")
            search_results = await self._collect_search_data(email)
            
            # Phase 4: Social media analysis
            logger.info("Phase 4: Social media analysis")
            social_data = await self._collect_social_data(email)
            
            # Phase 5: Academic intelligence (if enabled)
            academic_data = {}
            if self.enable_academic_analysis:
                logger.info("Phase 5: Academic intelligence")
                academic_data = await self._collect_academic_data(email)
            
            # Phase 6: Digital twin creation (if enabled)
            digital_twin_data = {}
            personality_data = {}
            network_data = {}
            if self.enable_digital_twin:
                logger.info("Phase 6: Digital twin creation")
                digital_twin_data, personality_data, network_data = await self._create_digital_twin(
                    email, general_data, academic_data, social_data
                )
            
            # Phase 7: Analysis and scoring
            logger.info("Phase 7: Analysis and scoring")
            scores = self._calculate_scores(general_data, academic_data, social_data, digital_twin_data)
            
            # Phase 8: Generate insights and recommendations
            logger.info("Phase 8: Generating insights")
            insights = self._generate_insights(email, general_data, academic_data, social_data, digital_twin_data)
            
            # Create comprehensive results
            processing_time = time.time() - self.start_time
            
            results = IntelligenceResults(
                email=email,
                analysis_timestamp=datetime.now().isoformat(),
                processing_time=processing_time,
                email_validation=email_validation,
                general_intelligence=general_data,
                search_results=search_results,
                social_profiles=social_data.get('profiles', []),
                academic_profile=academic_data.get('academic_profile', {}),
                academic_publications=academic_data.get('publications', []),
                academic_confidence=academic_data.get('confidence_scores', {}),
                digital_twin=digital_twin_data,
                personality_analysis=personality_data,
                network_analysis=network_data,
                overall_confidence_score=scores['overall_confidence'],
                data_completeness_score=scores['completeness'],
                verification_sources=self._get_verification_sources(general_data, academic_data, social_data),
                key_findings=insights['key_findings'],
                recommendations=insights['recommendations'],
                risk_indicators=insights['risk_indicators']
            )
            
            self.results = results
            logger.info(f"Analysis completed for {email} in {processing_time:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during analysis of {email}: {e}")
            processing_time = time.time() - self.start_time if self.start_time else 0
            return self._create_error_results(email, str(e), processing_time)

    async def _validate_email(self, email: str) -> Dict[str, Any]:
        """Phase 1: Validate email address"""
        try:
            # EmailValidator.validate_email is synchronous, not async
            validation_result = EmailValidator.validate_email(email)
            
            # Add additional checks
            domain = email.split('@')[1] if '@' in email else ''
            username = email.split('@')[0] if '@' in email else ''
            
            validation_result.update({
                'domain': domain,
                'username': username,
                'is_academic_domain': self._is_academic_domain(domain),
                'is_corporate_domain': self._is_corporate_domain(domain),
                'is_public_domain': self._is_public_domain(domain)
            })
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Email validation error: {e}")
            return {'is_valid': False, 'error': str(e)}

    async def _collect_general_data(self, email: str) -> Dict[str, Any]:
        """Phase 2: Collect general data using DataCollector"""
        try:
            collector = DataCollector(email)
            data = await collector.collect_all()
            
            # Enhance with additional metadata
            data['collection_timestamp'] = datetime.now().isoformat()
            data['collection_method'] = 'automated_system'
            
            return data
            
        except Exception as e:
            logger.error(f"General data collection error: {e}")
            return {'error': str(e), 'sources': []}

    async def _collect_search_data(self, email: str) -> List[Dict[str, Any]]:
        """Phase 3: Collect search engine data"""
        try:
            # Use SearchEngineManager for search data
            async with SearchEngineManager() as search_manager:
                search_query = f'"{email}"'
                engines = ['google', 'bing', 'duckduckgo']
                results = {}
                for engine in engines:
                    engine_results = await search_manager.search_single_engine(search_query, engine)
                    results[engine] = {'results': [asdict(r) for r in engine_results]}
            
            # Process and enhance results
            processed_results = []
            for engine, data in results.items():
                processed_results.append({
                    'engine': engine,
                    'timestamp': datetime.now().isoformat(),
                    'results_count': len(data.get('results', [])),
                    'data': data
                })
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Search data collection error: {e}")
            return []

    async def _collect_social_data(self, email: str) -> Dict[str, Any]:
        """Phase 4: Collect social media data"""
        try:
            # Use GoogleSearchCollector as a placeholder for social data
            social_collector = GoogleSearchCollector(email)
            data = await social_collector.collect()
            if data:
                data = {'profiles': data.get('social_profiles', []), 'platforms': {}}
            else:
                data = {'profiles': [], 'platforms': {}}
            
            # Enhance with metadata
            data['collection_timestamp'] = datetime.now().isoformat()
            data['platforms_searched'] = list(data.get('platforms', {}).keys())
            
            return data
            
        except Exception as e:
            logger.error(f"Social data collection error: {e}")
            return {'profiles': [], 'platforms': {}}

    async def _collect_academic_data(self, email: str) -> Dict[str, Any]:
        """Phase 5: Collect academic intelligence data"""
        try:
            academic_collector = AcademicIntelligenceCollector()
            data = await academic_collector.collect_academic_profile(email)
            
            # Add analysis metadata
            data['academic_analysis_timestamp'] = datetime.now().isoformat()
            data['analysis_version'] = '2.0'
            
            return data
            
        except Exception as e:
            logger.error(f"Academic data collection error: {e}")
            return {'academic_profile': {}, 'publications': [], 'confidence_scores': {}}

    async def _create_digital_twin(self, email: str, general_data: Dict, academic_data: Dict, social_data: Dict) -> Tuple[Dict, Dict, Dict]:
        """Phase 6: Create digital twin"""
        try:
            twin_creator = DigitalTwinCreator()
            
            # Combine all data for twin creation
            combined_data = {
                'general': general_data,
                'academic': academic_data,
                'social': social_data
            }
            
            # Create digital twin with available data
            if academic_data.get('academic_profile'):
                digital_twin = twin_creator.create_digital_twin(email, academic_data, academic_data.get('search_results', []))
            else:
                # Create a basic twin from available data
                digital_twin = {'email': email, 'basic_profile': combined_data}
            
            # Extract components
            twin_data = digital_twin.to_dict() if hasattr(digital_twin, 'to_dict') else digital_twin
            personality_data = twin_data.get('personality_profile', {})
            network_data = twin_data.get('network_analysis', {})
            
            return twin_data, personality_data, network_data
            
        except Exception as e:
            logger.error(f"Digital twin creation error: {e}")
            return {}, {}, {}

    def _calculate_scores(self, general_data: Dict, academic_data: Dict, social_data: Dict, digital_twin_data: Dict) -> Dict[str, float]:
        """Calculate confidence and completeness scores"""
        try:
            # Overall confidence score
            confidence_factors = []
            
            # General data confidence
            if general_data.get('person_info'):
                confidence_factors.append(0.3)
            if general_data.get('sources'):
                confidence_factors.append(0.2 * min(len(general_data['sources']) / 5, 1.0))
            
            # Academic confidence
            if academic_data.get('academic_profile'):
                confidence_factors.append(0.3)
            if academic_data.get('confidence_scores'):
                avg_academic_confidence = sum(academic_data['confidence_scores'].values()) / len(academic_data['confidence_scores'])
                confidence_factors.append(0.2 * avg_academic_confidence)
            
            # Social confidence
            if social_data.get('profiles'):
                confidence_factors.append(0.2 * min(len(social_data['profiles']) / 3, 1.0))
            
            overall_confidence = sum(confidence_factors) if confidence_factors else 0.0
            
            # Completeness score
            completeness_factors = [
                bool(general_data.get('person_info', {}).get('name')),
                bool(general_data.get('person_info', {}).get('location')),
                bool(academic_data.get('academic_profile')),
                bool(social_data.get('profiles')),
                bool(digital_twin_data),
                bool(general_data.get('phone_numbers')),
                bool(general_data.get('websites'))
            ]
            
            completeness_score = sum(completeness_factors) / len(completeness_factors)
            
            return {
                'overall_confidence': min(overall_confidence, 1.0),
                'completeness': completeness_score
            }
            
        except Exception as e:
            logger.error(f"Score calculation error: {e}")
            return {'overall_confidence': 0.0, 'completeness': 0.0}

    def _generate_insights(self, email: str, general_data: Dict, academic_data: Dict, social_data: Dict, digital_twin_data: Dict) -> Dict[str, List[str]]:
        """Generate insights, recommendations, and risk indicators"""
        try:
            key_findings = []
            recommendations = []
            risk_indicators = []
            
            # Analyze findings
            if general_data.get('person_info', {}).get('name'):
                key_findings.append(f"Identified person: {general_data['person_info']['name']}")
            
            if academic_data.get('academic_profile', {}).get('institution'):
                key_findings.append(f"Academic affiliation: {academic_data['academic_profile']['institution']}")
            
            if social_data.get('profiles'):
                key_findings.append(f"Found {len(social_data['profiles'])} social media profiles")
            
            # Generate recommendations
            if not general_data.get('person_info', {}).get('name'):
                recommendations.append("Consider expanding search parameters to find identity information")
            
            if not academic_data.get('academic_profile'):
                recommendations.append("Academic analysis may benefit from additional data sources")
            
            if len(social_data.get('profiles', [])) < 2:
                recommendations.append("Social media presence appears limited - consider privacy-conscious individual")
            
            # Identify risk indicators
            if not general_data.get('sources'):
                risk_indicators.append("Very limited public information available")
            
            if self._check_suspicious_patterns(email, general_data):
                risk_indicators.append("Potentially suspicious patterns detected")
            
            return {
                'key_findings': key_findings,
                'recommendations': recommendations,
                'risk_indicators': risk_indicators
            }
            
        except Exception as e:
            logger.error(f"Insight generation error: {e}")
            return {'key_findings': [], 'recommendations': [], 'risk_indicators': []}

    def _get_verification_sources(self, general_data: Dict, academic_data: Dict, social_data: Dict) -> List[str]:
        """Get list of verification sources used"""
        sources = []
        
        if general_data.get('sources'):
            sources.extend(['general_search', 'web_scraping'])
        
        if academic_data.get('academic_profile'):
            sources.append('academic_databases')
        
        if social_data.get('profiles'):
            sources.append('social_media')
        
        return list(set(sources))

    def _is_academic_domain(self, domain: str) -> bool:
        """Check if domain is academic"""
        academic_tlds = ['.edu', '.ac.', '.uni-', '.university']
        return any(tld in domain.lower() for tld in academic_tlds)

    def _is_corporate_domain(self, domain: str) -> bool:
        """Check if domain is corporate"""
        public_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'mail.ru', 'yandex.ru']
        return domain.lower() not in public_domains and '.' in domain

    def _is_public_domain(self, domain: str) -> bool:
        """Check if domain is public email provider"""
        public_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'mail.ru', 'yandex.ru']
        return domain.lower() in public_domains

    def _check_suspicious_patterns(self, email: str, general_data: Dict) -> bool:
        """Check for suspicious patterns"""
        # Simple heuristics for suspicious activity
        suspicious_indicators = [
            len(general_data.get('sources', [])) == 0,  # No public information
            '@' not in email,  # Invalid email format
            len(email.split('@')[0]) < 3 if '@' in email else True,  # Very short username
        ]
        
        return sum(suspicious_indicators) >= 2

    def _create_minimal_results(self, email: str, validation: Dict) -> IntelligenceResults:
        """Create minimal results for invalid emails"""
        return IntelligenceResults(
            email=email,
            analysis_timestamp=datetime.now().isoformat(),
            processing_time=time.time() - self.start_time if self.start_time else 0,
            email_validation=validation,
            general_intelligence={},
            search_results=[],
            social_profiles=[],
            academic_profile={},
            academic_publications=[],
            academic_confidence={},
            digital_twin={},
            personality_analysis={},
            network_analysis={},
            overall_confidence_score=0.0,
            data_completeness_score=0.0,
            verification_sources=[],
            key_findings=["Email validation failed"],
            recommendations=["Verify email address format and try again"],
            risk_indicators=["Invalid email format"]
        )

    def _create_error_results(self, email: str, error: str, processing_time: float) -> IntelligenceResults:
        """Create error results"""
        return IntelligenceResults(
            email=email,
            analysis_timestamp=datetime.now().isoformat(),
            processing_time=processing_time,
            email_validation={'is_valid': False, 'error': error},
            general_intelligence={},
            search_results=[],
            social_profiles=[],
            academic_profile={},
            academic_publications=[],
            academic_confidence={},
            digital_twin={},
            personality_analysis={},
            network_analysis={},
            overall_confidence_score=0.0,
            data_completeness_score=0.0,
            verification_sources=[],
            key_findings=[f"Analysis failed: {error}"],
            recommendations=["Try again later or contact support"],
            risk_indicators=["Analysis error occurred"]
        )

    def save_results(self, output_path: str) -> None:
        """Save analysis results to file"""
        if not self.results:
            logger.warning("No results to save")
            return
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.results), f, ensure_ascii=False, indent=2)
            
            logger.info(f"Results saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")

    def generate_report(self) -> str:
        """Generate human-readable report"""
        if not self.results:
            return "No analysis results available"
        
        try:
            report = f"""
# Comprehensive Email Intelligence Report

## Analysis Summary
- **Target Email:** {self.results.email}
- **Analysis Date:** {self.results.analysis_timestamp}
- **Processing Time:** {self.results.processing_time:.2f} seconds
- **Overall Confidence:** {self.results.overall_confidence_score:.2f}/1.0
- **Data Completeness:** {self.results.data_completeness_score:.2f}/1.0

## Email Validation
- **Valid:** {self.results.email_validation.get('is_valid', False)}
- **Domain Type:** {self._get_domain_type()}

## Key Findings
{self._format_list(self.results.key_findings)}

## Academic Profile
- **Institution:** {self.results.academic_profile.get('institution', 'Not found')}
- **Publications:** {len(self.results.academic_publications)}
- **ORCID:** {self.results.academic_profile.get('orcid_id', 'Not found')}

## Social Media Presence
- **Profiles Found:** {len(self.results.social_profiles)}
- **Platforms:** {', '.join([p.get('platform', 'Unknown') for p in self.results.social_profiles])}

## Digital Twin Analysis
- **Personality Type:** {self.results.personality_analysis.get('type', 'Not determined')}
- **Network Size:** {self.results.network_analysis.get('network_size', 0)}

## Verification Sources
{self._format_list(self.results.verification_sources)}

## Recommendations
{self._format_list(self.results.recommendations)}

## Risk Indicators
{self._format_list(self.results.risk_indicators)}

---
*Generated by Automated Email Intelligence System*
"""
            return report
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return f"Error generating report: {e}"

    def _get_domain_type(self) -> str:
        """Get domain type description"""
        validation = self.results.email_validation
        if validation.get('is_academic_domain'):
            return "Academic"
        elif validation.get('is_corporate_domain'):
            return "Corporate"
        elif validation.get('is_public_domain'):
            return "Public Email Provider"
        else:
            return "Unknown"

    def _format_list(self, items: List[str]) -> str:
        """Format list items for report"""
        if not items:
            return "- None"
        return '\n'.join([f"- {item}" for item in items])


# Convenience function for quick analysis
async def analyze_email_comprehensive(email: str, config: Optional[Dict] = None) -> IntelligenceResults:
    """
    Convenience function to perform comprehensive email analysis
    
    Args:
        email: Email address to analyze
        config: Optional configuration parameters
        
    Returns:
        IntelligenceResults: Comprehensive analysis results
    """
    system = AutomatedIntelligenceSystem(config)
    return await system.analyze_email(email)


# Example usage and testing
async def main():
    """Example usage of the Automated Intelligence System"""
    
    # Configuration
    config = {
        'max_processing_time': 300,
        'enable_deep_search': True,
        'enable_academic_analysis': True,
        'enable_social_analysis': True,
        'enable_digital_twin': True,
        'request_delay': 1.0
    }
    
    # Test email
    test_email = "buch1202@mail.ru"
    
    # Initialize system
    system = AutomatedIntelligenceSystem(config)
    
    # Perform analysis
    logger.info(f"Starting comprehensive analysis for {test_email}")
    results = await system.analyze_email(test_email)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"/tmp/comprehensive_analysis_{test_email.replace('@', '_at_')}_{timestamp}.json"
    system.save_results(output_path)
    
    # Generate and save report
    report = system.generate_report()
    report_path = f"/tmp/comprehensive_report_{test_email.replace('@', '_at_')}_{timestamp}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Display summary
    print("\n" + "="*80)
    print("COMPREHENSIVE EMAIL INTELLIGENCE ANALYSIS COMPLETE")
    print("="*80)
    print(f"Email: {test_email}")
    print(f"Processing Time: {results.processing_time:.2f}s")
    print(f"Confidence Score: {results.overall_confidence_score:.2f}")
    print(f"Completeness Score: {results.data_completeness_score:.2f}")
    print(f"Key Findings: {len(results.key_findings)}")
    print(f"Verification Sources: {len(results.verification_sources)}")
    print("\nFiles generated:")
    print(f"- Detailed Results: {output_path}")
    print(f"- Human Report: {report_path}")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
