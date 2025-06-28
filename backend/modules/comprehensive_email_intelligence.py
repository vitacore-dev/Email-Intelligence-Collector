import logging
from .data_collector import DataCollector
from .academic_intelligence import AcademicIntelligenceCollector
from .digital_twin import DigitalTwinCreator
from .social_collectors import SocialCollector

logger = logging.getLogger(__name__)

class ComprehensiveEmailIntelligence:
    def __init__(self, email: str):
        self.email = email

    async def run_analysis(self):
        # Collect general data
        data_collector = DataCollector(self.email)
        general_data = await data_collector.collect_all()

        # Academic intelligence
        academic_collector = AcademicIntelligenceCollector()
        academic_data = await academic_collector.collect_academic_profile(self.email)

        # Social intelligence
        social_collector = SocialCollector(self.email)
        social_data = await social_collector.collect_social_data()

        # Create digital twin
        twin_creator = DigitalTwinCreator()
        digital_twin = twin_creator.create_digital_twin(
            self.email, academic_data, social_data
        )

        # Log and return results
        logger.info(f"Analysis complete for {self.email}")
        return {
            "general_data": general_data,
            "academic_data": academic_data,
            "social_data": social_data,
            "digital_twin": digital_twin,
        }
