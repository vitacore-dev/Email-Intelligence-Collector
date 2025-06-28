"""
Модуль для создания цифрового двойника на основе собранных академических и личных данных
Генерирует детальный профиль с визуализацией и анализом
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from collections import Counter, defaultdict
import logging
import hashlib
import base64

logger = logging.getLogger(__name__)

@dataclass
class PersonalityProfile:
    """Профиль личности на основе анализа данных"""
    communication_style: str = "unknown"  # formal, casual, academic, friendly
    expertise_level: str = "unknown"  # novice, intermediate, expert, authority
    collaboration_tendency: str = "unknown"  # individual, collaborative, leader
    research_focus: str = "unknown"  # theoretical, applied, interdisciplinary
    career_stage: str = "unknown"  # student, early-career, mid-career, senior, emeritus
    digital_presence: str = "unknown"  # minimal, moderate, active, prominent
    
@dataclass
class NetworkAnalysis:
    """Анализ сети связей"""
    collaborators: List[str] = field(default_factory=list)
    institutions: List[str] = field(default_factory=list)
    research_communities: List[str] = field(default_factory=list)
    influence_score: float = 0.0
    centrality_score: float = 0.0
    network_size: int = 0
    
@dataclass
class CareerTrajectory:
    """Траектория карьеры"""
    career_milestones: List[Dict[str, Any]] = field(default_factory=list)
    career_progression: str = "unknown"  # ascending, stable, transitioning
    experience_years: Optional[int] = None
    career_changes: List[str] = field(default_factory=list)
    specialization_evolution: List[str] = field(default_factory=list)
    
@dataclass
class ImpactMetrics:
    """Метрики влияния и воздействия"""
    citation_impact: Dict[str, Any] = field(default_factory=dict)
    research_impact: Dict[str, Any] = field(default_factory=dict)
    teaching_impact: Dict[str, Any] = field(default_factory=dict)
    industry_impact: Dict[str, Any] = field(default_factory=dict)
    social_impact: Dict[str, Any] = field(default_factory=dict)
    overall_impact_score: float = 0.0
    
@dataclass
class DigitalTwin:
    """Цифровой двойник персоны"""
    # Основная информация
    email: str = ""
    name: Optional[str] = None
    primary_affiliation: Optional[str] = None
    
    # Академический профиль
    academic_profile: Dict[str, Any] = field(default_factory=dict)
    
    # Анализ личности и поведения
    personality_profile: PersonalityProfile = field(default_factory=PersonalityProfile)
    
    # Сетевой анализ
    network_analysis: NetworkAnalysis = field(default_factory=NetworkAnalysis)
    
    # Карьерная траектория
    career_trajectory: CareerTrajectory = field(default_factory=CareerTrajectory)
    
    # Метрики воздействия
    impact_metrics: ImpactMetrics = field(default_factory=ImpactMetrics)
    
    # Визуализация данных
    visualization_data: Dict[str, Any] = field(default_factory=dict)
    
    # Метаданные
    creation_timestamp: str = ""
    confidence_score: float = 0.0
    data_sources: List[str] = field(default_factory=list)
    completeness_score: float = 0.0

class PersonalityAnalyzer:
    """Анализатор личности на основе текстовых данных"""
    
    def __init__(self):
        # Паттерны для определения стиля коммуникации
        self.communication_patterns = {
            'formal': [
                r'\b(?:furthermore|moreover|consequently|therefore|nevertheless)\b',
                r'\b(?:Dr\.|Prof\.|Professor)\b',
                r'\b(?:research|study|investigation|analysis|examination)\b',
                r'\b(?:results|findings|conclusions|implications)\b'
            ],
            'casual': [
                r'\b(?:cool|awesome|great|amazing|fantastic)\b',
                r'\b(?:hey|hi|hello|thanks|cheers)\b',
                r'\b(?:stuff|things|pretty|really|super)\b'
            ],
            'academic': [
                r'\b(?:hypothesis|methodology|literature|empirical|theoretical)\b',
                r'\b(?:publication|journal|conference|proceedings)\b',
                r'\b(?:significant|correlation|statistical|experimental)\b'
            ]
        }
        
        # Паттерны для определения уровня экспертизы
        self.expertise_patterns = {
            'authority': [
                r'\b(?:pioneer|leader|expert|authority|renowned)\b',
                r'\b(?:established|recognized|distinguished|eminent)\b',
                r'\b(?:founding|groundbreaking|seminal|influential)\b'
            ],
            'expert': [
                r'\b(?:experienced|skilled|proficient|specialist)\b',
                r'\b(?:advanced|sophisticated|comprehensive|extensive)\b',
                r'\b(?:developed|created|designed|implemented)\b'
            ],
            'intermediate': [
                r'\b(?:working|learning|developing|exploring)\b',
                r'\b(?:interested|focused|studying|researching)\b'
            ]
        }
        
    def analyze_personality(self, text_data: List[str], academic_profile: Dict[str, Any]) -> PersonalityProfile:
        """Анализ личности на основе текстовых данных"""
        profile = PersonalityProfile()
        
        # Объединяем весь текст
        all_text = ' '.join(text_data).lower()
        
        # Анализ стиля коммуникации
        profile.communication_style = self._analyze_communication_style(all_text)
        
        # Анализ уровня экспертизы
        profile.expertise_level = self._analyze_expertise_level(all_text, academic_profile)
        
        # Анализ склонности к сотрудничеству
        profile.collaboration_tendency = self._analyze_collaboration_tendency(all_text)
        
        # Анализ фокуса исследований
        profile.research_focus = self._analyze_research_focus(all_text)
        
        # Определение стадии карьеры
        profile.career_stage = self._determine_career_stage(academic_profile)
        
        # Анализ цифрового присутствия
        profile.digital_presence = self._analyze_digital_presence(academic_profile)
        
        return profile
    
    def _analyze_communication_style(self, text: str) -> str:
        """Анализ стиля коммуникации"""
        scores = {}
        
        for style, patterns in self.communication_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                score += len(matches)
            scores[style] = score
        
        if not scores or max(scores.values()) == 0:
            return "unknown"
        
        return max(scores, key=scores.get)
    
    def _analyze_expertise_level(self, text: str, academic_profile: Dict[str, Any]) -> str:
        """Анализ уровня экспертизы"""
        scores = {}
        
        # Анализ текста
        for level, patterns in self.expertise_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                score += len(matches)
            scores[level] = score
        
        # Дополнительные факторы из академического профиля
        degrees = academic_profile.get('degrees', [])
        positions = academic_profile.get('positions', [])
        publications = academic_profile.get('publications', [])
        
        # PhD добавляет к экспертизе
        if any('phd' in deg.get('degree', '').lower() for deg in degrees):
            scores['expert'] = scores.get('expert', 0) + 2
        
        # Профессорские должности
        if any('professor' in pos.get('position', '').lower() for pos in positions):
            scores['authority'] = scores.get('authority', 0) + 3
        
        # Количество публикаций
        if len(publications) > 10:
            scores['authority'] = scores.get('authority', 0) + 2
        elif len(publications) > 5:
            scores['expert'] = scores.get('expert', 0) + 1
        
        if not scores or max(scores.values()) == 0:
            return "unknown"
        
        return max(scores, key=scores.get)
    
    def _analyze_collaboration_tendency(self, text: str) -> str:
        """Анализ склонности к сотрудничеству"""
        collaboration_keywords = ['collaboration', 'team', 'joint', 'together', 'partner']
        leadership_keywords = ['lead', 'director', 'head', 'chair', 'chief']
        individual_keywords = ['independent', 'solo', 'individual', 'personal']
        
        collab_score = sum(text.count(keyword) for keyword in collaboration_keywords)
        leader_score = sum(text.count(keyword) for keyword in leadership_keywords)
        individual_score = sum(text.count(keyword) for keyword in individual_keywords)
        
        if leader_score > collab_score and leader_score > individual_score:
            return "leader"
        elif collab_score > individual_score:
            return "collaborative"
        elif individual_score > 0:
            return "individual"
        else:
            return "unknown"
    
    def _analyze_research_focus(self, text: str) -> str:
        """Анализ фокуса исследований"""
        theoretical_keywords = ['theory', 'theoretical', 'model', 'framework', 'concept']
        applied_keywords = ['application', 'practical', 'implementation', 'real-world', 'industry']
        interdisciplinary_keywords = ['interdisciplinary', 'multidisciplinary', 'cross-disciplinary']
        
        theoretical_score = sum(text.count(keyword) for keyword in theoretical_keywords)
        applied_score = sum(text.count(keyword) for keyword in applied_keywords)
        interdisciplinary_score = sum(text.count(keyword) for keyword in interdisciplinary_keywords)
        
        if interdisciplinary_score > 0:
            return "interdisciplinary"
        elif applied_score > theoretical_score:
            return "applied"
        elif theoretical_score > 0:
            return "theoretical"
        else:
            return "unknown"
    
    def _determine_career_stage(self, academic_profile: Dict[str, Any]) -> str:
        """Определение стадии карьеры"""
        positions = academic_profile.get('positions', [])
        degrees = academic_profile.get('degrees', [])
        
        if not positions and not degrees:
            return "unknown"
        
        # Анализ должностей
        for position in positions:
            pos_title = position.get('position', '').lower()
            if 'emeritus' in pos_title:
                return "emeritus"
            elif 'professor' in pos_title and 'assistant' not in pos_title and 'associate' not in pos_title:
                return "senior"
            elif 'associate professor' in pos_title:
                return "mid-career"
            elif 'assistant professor' in pos_title:
                return "early-career"
            elif any(term in pos_title for term in ['student', 'phd', 'doctoral']):
                return "student"
        
        # Если нет четких должностей, анализируем степени
        has_phd = any('phd' in deg.get('degree', '').lower() for deg in degrees)
        if has_phd:
            return "early-career"
        
        return "unknown"
    
    def _analyze_digital_presence(self, academic_profile: Dict[str, Any]) -> str:
        """Анализ цифрового присутствия"""
        websites = academic_profile.get('academic_websites', [])
        social_profiles = academic_profile.get('social_profiles', [])
        
        total_presence = len(websites) + len(social_profiles)
        
        if total_presence >= 5:
            return "prominent"
        elif total_presence >= 3:
            return "active"
        elif total_presence >= 1:
            return "moderate"
        else:
            return "minimal"

class NetworkAnalyzer:
    """Анализатор сетевых связей"""
    
    def analyze_network(self, academic_profile: Dict[str, Any], search_results: List[Dict[str, Any]]) -> NetworkAnalysis:
        """Анализ сетевых связей"""
        analysis = NetworkAnalysis()
        
        # Извлекаем коллабораторов из публикаций
        analysis.collaborators = self._extract_collaborators(academic_profile.get('publications', []))
        
        # Анализируем институции
        analysis.institutions = academic_profile.get('institutions', [])
        
        # Определяем исследовательские сообщества
        analysis.research_communities = self._identify_research_communities(
            academic_profile.get('research_areas', [])
        )
        
        # Вычисляем метрики сети
        analysis.network_size = len(analysis.collaborators) + len(analysis.institutions)
        analysis.influence_score = self._calculate_influence_score(academic_profile, search_results)
        analysis.centrality_score = self._calculate_centrality_score(analysis)
        
        return analysis
    
    def _extract_collaborators(self, publications: List[Dict[str, Any]]) -> List[str]:
        """Извлечение коллабораторов из публикаций"""
        collaborators = []
        
        for pub in publications:
            context = pub.get('context', '')
            # Простой поиск имен в контексте публикаций
            name_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
            names = re.findall(name_pattern, context)
            collaborators.extend(names)
        
        # Удаляем дубликаты и возвращаем топ-10
        return list(set(collaborators))[:10]
    
    def _identify_research_communities(self, research_areas: List[str]) -> List[str]:
        """Идентификация исследовательских сообществ"""
        # Упрощенное сопоставление областей с сообществами
        community_mapping = {
            'Computer Science': ['ACM', 'IEEE Computer Society'],
            'Machine Learning': ['ICML', 'NeurIPS', 'ICLR'],
            'Biology': ['Society for Molecular Biology', 'American Society for Cell Biology'],
            'Physics': ['American Physical Society', 'Institute of Physics'],
            'Medicine': ['American Medical Association', 'World Health Organization']
        }
        
        communities = []
        for area in research_areas:
            for field, comms in community_mapping.items():
                if field.lower() in area.lower():
                    communities.extend(comms)
        
        return list(set(communities))
    
    def _calculate_influence_score(self, academic_profile: Dict[str, Any], search_results: List[Dict[str, Any]]) -> float:
        """Расчет показателя влияния"""
        score = 0.0
        
        # Публикации
        publications = academic_profile.get('publications', [])
        score += len(publications) * 0.1
        
        # Академические платформы
        websites = academic_profile.get('academic_websites', [])
        score += len(websites) * 0.2
        
        # Результаты поиска с высоким академическим скорингом
        high_score_results = [r for r in search_results if r.get('academic_score', 0) > 0.6]
        score += len(high_score_results) * 0.15
        
        # Должности
        positions = academic_profile.get('positions', [])
        for position in positions:
            if 'professor' in position.get('position', '').lower():
                score += 0.3
        
        return min(1.0, score)
    
    def _calculate_centrality_score(self, analysis: NetworkAnalysis) -> float:
        """Расчет показателя центральности в сети"""
        # Упрощенный расчет на основе размера сети
        if analysis.network_size == 0:
            return 0.0
        
        # Нормализуем относительно максимального возможного размера сети
        max_network_size = 50  # предполагаемый максимум
        return min(1.0, analysis.network_size / max_network_size)

class CareerAnalyzer:
    """Анализатор карьерной траектории"""
    
    def analyze_career(self, academic_profile: Dict[str, Any]) -> CareerTrajectory:
        """Анализ карьерной траектории"""
        trajectory = CareerTrajectory()
        
        # Извлекаем вехи карьеры
        trajectory.career_milestones = self._extract_career_milestones(academic_profile)
        
        # Анализируем прогрессию карьеры
        trajectory.career_progression = self._analyze_career_progression(trajectory.career_milestones)
        
        # Оцениваем опыт
        trajectory.experience_years = self._estimate_experience_years(academic_profile)
        
        # Выявляем изменения в карьере
        trajectory.career_changes = self._identify_career_changes(academic_profile)
        
        # Анализируем эволюцию специализации
        trajectory.specialization_evolution = self._analyze_specialization_evolution(academic_profile)
        
        return trajectory
    
    def _extract_career_milestones(self, academic_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Извлечение ключевых моментов карьеры"""
        milestones = []
        
        # Степени как вехи
        for degree in academic_profile.get('degrees', []):
            if degree.get('year'):
                milestones.append({
                    'type': 'degree',
                    'year': degree['year'],
                    'description': f"{degree['degree']} from {degree.get('university', 'Unknown')}",
                    'importance': self._get_degree_importance(degree['degree'])
                })
        
        # Должности как вехи
        for position in academic_profile.get('positions', []):
            milestones.append({
                'type': 'position',
                'year': 'unknown',  # Обычно не указан год в наших данных
                'description': f"{position['position']} at {position.get('university', 'Unknown')}",
                'importance': self._get_position_importance(position['position'])
            })
        
        # Сортируем по году (известные года в начале)
        milestones.sort(key=lambda x: (x['year'] == 'unknown', x['year']))
        
        return milestones
    
    def _get_degree_importance(self, degree: str) -> int:
        """Оценка важности степени (1-5)"""
        degree_lower = degree.lower()
        if 'phd' in degree_lower or 'doctor' in degree_lower:
            return 5
        elif 'master' in degree_lower or 'mba' in degree_lower:
            return 3
        elif 'bachelor' in degree_lower:
            return 2
        else:
            return 1
    
    def _get_position_importance(self, position: str) -> int:
        """Оценка важности должности (1-5)"""
        position_lower = position.lower()
        if any(title in position_lower for title in ['professor', 'dean', 'chair']):
            return 5
        elif 'researcher' in position_lower or 'scientist' in position_lower:
            return 3
        elif 'student' in position_lower:
            return 1
        else:
            return 2
    
    def _analyze_career_progression(self, milestones: List[Dict[str, Any]]) -> str:
        """Анализ прогрессии карьеры"""
        if len(milestones) < 2:
            return "unknown"
        
        # Анализируем тренд важности вех
        importance_trend = [m['importance'] for m in milestones if m['year'] != 'unknown']
        
        if len(importance_trend) < 2:
            return "stable"
        
        # Проверяем на восходящий тренд
        ascending = sum(1 for i in range(1, len(importance_trend)) 
                       if importance_trend[i] > importance_trend[i-1])
        
        if ascending >= len(importance_trend) * 0.6:
            return "ascending"
        elif ascending <= len(importance_trend) * 0.2:
            return "transitioning"
        else:
            return "stable"
    
    def _estimate_experience_years(self, academic_profile: Dict[str, Any]) -> Optional[int]:
        """Оценка лет опыта"""
        degrees = academic_profile.get('degrees', [])
        
        # Ищем самую раннюю степень с годом
        earliest_year = None
        for degree in degrees:
            if degree.get('year') and degree['year'].isdigit():
                year = int(degree['year'])
                if earliest_year is None or year < earliest_year:
                    earliest_year = year
        
        if earliest_year:
            current_year = datetime.now().year
            return current_year - earliest_year
        
        return None
    
    def _identify_career_changes(self, academic_profile: Dict[str, Any]) -> List[str]:
        """Выявление изменений в карьере"""
        changes = []
        
        institutions = academic_profile.get('institutions', [])
        if len(institutions) > 1:
            changes.append(f"Institution changes: {len(institutions)} different institutions")
        
        research_areas = academic_profile.get('research_areas', [])
        if len(research_areas) > 3:
            changes.append(f"Diverse research interests: {len(research_areas)} areas")
        
        return changes
    
    def _analyze_specialization_evolution(self, academic_profile: Dict[str, Any]) -> List[str]:
        """Анализ эволюции специализации"""
        research_areas = academic_profile.get('research_areas', [])
        
        # Упрощенный анализ - возвращаем области в порядке предполагаемой эволюции
        return research_areas[:5]  # Топ-5 областей

class ImpactAnalyzer:
    """Анализатор воздействия и влияния"""
    
    def analyze_impact(self, academic_profile: Dict[str, Any], 
                      search_results: List[Dict[str, Any]]) -> ImpactMetrics:
        """Анализ воздействия"""
        metrics = ImpactMetrics()
        
        # Анализ влияния публикаций
        metrics.citation_impact = self._analyze_citation_impact(academic_profile)
        
        # Анализ исследовательского воздействия
        metrics.research_impact = self._analyze_research_impact(academic_profile, search_results)
        
        # Анализ преподавательского воздействия
        metrics.teaching_impact = self._analyze_teaching_impact(academic_profile)
        
        # Анализ влияния на индустрию
        metrics.industry_impact = self._analyze_industry_impact(academic_profile)
        
        # Анализ социального воздействия
        metrics.social_impact = self._analyze_social_impact(academic_profile, search_results)
        
        # Общий показатель воздействия
        metrics.overall_impact_score = self._calculate_overall_impact(metrics)
        
        return metrics
    
    def _analyze_citation_impact(self, academic_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ влияния через цитирования"""
        publications = academic_profile.get('publications', [])
        
        return {
            'publication_count': len(publications),
            'estimated_citations': len(publications) * 5,  # Примерная оценка
            'h_index_estimate': min(len(publications), 10),  # Упрощенная оценка
            'publication_venues': list(set([p.get('journal', 'Unknown') for p in publications]))
        }
    
    def _analyze_research_impact(self, academic_profile: Dict[str, Any], 
                                search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ исследовательского воздействия"""
        research_areas = academic_profile.get('research_areas', [])
        high_impact_results = [r for r in search_results if r.get('academic_score', 0) > 0.7]
        
        return {
            'research_breadth': len(research_areas),
            'research_visibility': len(high_impact_results),
            'interdisciplinary_scope': len([area for area in research_areas 
                                          if 'interdisciplinary' in area.lower()]),
            'innovation_indicators': self._count_innovation_indicators(search_results)
        }
    
    def _analyze_teaching_impact(self, academic_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ преподавательского воздействия"""
        positions = academic_profile.get('positions', [])
        teaching_positions = [p for p in positions 
                            if any(term in p.get('position', '').lower() 
                                  for term in ['professor', 'lecturer', 'instructor'])]
        
        return {
            'teaching_positions': len(teaching_positions),
            'educational_impact_estimate': len(teaching_positions) * 2,
            'institutions_taught': len(set([p.get('university', '') for p in teaching_positions]))
        }
    
    def _analyze_industry_impact(self, academic_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ влияния на индустрию"""
        research_areas = academic_profile.get('research_areas', [])
        applied_areas = [area for area in research_areas 
                        if any(term in area.lower() 
                              for term in ['engineering', 'technology', 'application', 'industry'])]
        
        return {
            'applied_research_areas': len(applied_areas),
            'industry_relevance_score': min(1.0, len(applied_areas) / 5.0),
            'potential_applications': applied_areas
        }
    
    def _analyze_social_impact(self, academic_profile: Dict[str, Any], 
                              search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ социального воздействия"""
        social_websites = academic_profile.get('academic_websites', [])
        public_engagement = len([r for r in search_results 
                               if any(term in r.get('snippet', '').lower() 
                                     for term in ['public', 'society', 'community', 'outreach'])])
        
        return {
            'digital_presence': len(social_websites),
            'public_engagement_score': public_engagement,
            'social_media_activity': len([w for w in social_websites 
                                         if any(platform in w 
                                               for platform in ['twitter', 'linkedin', 'facebook'])])
        }
    
    def _count_innovation_indicators(self, search_results: List[Dict[str, Any]]) -> int:
        """Подсчет индикаторов инновационности"""
        innovation_terms = ['innovative', 'breakthrough', 'novel', 'pioneering', 
                           'groundbreaking', 'revolutionary', 'cutting-edge']
        
        count = 0
        for result in search_results:
            text = (result.get('title', '') + ' ' + result.get('snippet', '')).lower()
            count += sum(1 for term in innovation_terms if term in text)
        
        return count
    
    def _calculate_overall_impact(self, metrics: ImpactMetrics) -> float:
        """Расчет общего показателя воздействия"""
        # Простая формула для объединения различных метрик
        citation_score = min(1.0, metrics.citation_impact.get('publication_count', 0) / 20.0)
        research_score = min(1.0, metrics.research_impact.get('research_visibility', 0) / 10.0)
        teaching_score = min(1.0, metrics.teaching_impact.get('teaching_positions', 0) / 5.0)
        industry_score = metrics.industry_impact.get('industry_relevance_score', 0.0)
        social_score = min(1.0, metrics.social_impact.get('public_engagement_score', 0) / 5.0)
        
        return (citation_score + research_score + teaching_score + industry_score + social_score) / 5.0

class VisualizationDataGenerator:
    """Генератор данных для визуализации"""
    
    def generate_visualization_data(self, digital_twin: DigitalTwin) -> Dict[str, Any]:
        """Генерация данных для визуализации"""
        return {
            'profile_summary': self._generate_profile_summary(digital_twin),
            'skill_radar': self._generate_skill_radar(digital_twin),
            'career_timeline': self._generate_career_timeline(digital_twin),
            'network_graph': self._generate_network_graph(digital_twin),
            'impact_metrics': self._generate_impact_visualization(digital_twin),
            'research_areas_cloud': self._generate_research_cloud(digital_twin),
            'collaboration_network': self._generate_collaboration_network(digital_twin),
            'publication_trends': self._generate_publication_trends(digital_twin)
        }
    
    def _generate_profile_summary(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Генерация сводки профиля"""
        return {
            'name': twin.name or 'Unknown',
            'email': twin.email,
            'primary_affiliation': twin.primary_affiliation or 'Unknown',
            'career_stage': twin.personality_profile.career_stage,
            'expertise_level': twin.personality_profile.expertise_level,
            'confidence_score': twin.confidence_score,
            'completeness_score': twin.completeness_score
        }
    
    def _generate_skill_radar(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Генерация радарной диаграммы навыков"""
        return {
            'categories': [
                'Research Excellence',
                'Teaching Impact',
                'Industry Relevance',
                'Collaboration',
                'Innovation',
                'Digital Presence'
            ],
            'values': [
                twin.impact_metrics.research_impact.get('research_visibility', 0) / 10.0,
                twin.impact_metrics.teaching_impact.get('teaching_positions', 0) / 5.0,
                twin.impact_metrics.industry_impact.get('industry_relevance_score', 0),
                min(1.0, twin.network_analysis.network_size / 20.0),
                min(1.0, twin.impact_metrics.research_impact.get('innovation_indicators', 0) / 5.0),
                min(1.0, twin.impact_metrics.social_impact.get('digital_presence', 0) / 5.0)
            ]
        }
    
    def _generate_career_timeline(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Генерация временной линии карьеры"""
        milestones = twin.career_trajectory.career_milestones
        
        return {
            'events': [
                {
                    'year': m['year'],
                    'type': m['type'],
                    'description': m['description'],
                    'importance': m['importance']
                }
                for m in milestones
            ],
            'career_progression': twin.career_trajectory.career_progression,
            'experience_years': twin.career_trajectory.experience_years
        }
    
    def _generate_network_graph(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Генерация сетевого графа"""
        return {
            'nodes': [
                {'id': twin.email, 'label': twin.name or twin.email, 'type': 'person', 'size': 10}
            ] + [
                {'id': inst, 'label': inst, 'type': 'institution', 'size': 5}
                for inst in twin.network_analysis.institutions
            ] + [
                {'id': collab, 'label': collab, 'type': 'collaborator', 'size': 3}
                for collab in twin.network_analysis.collaborators[:10]
            ],
            'edges': [
                {'from': twin.email, 'to': inst, 'type': 'affiliation'}
                for inst in twin.network_analysis.institutions
            ] + [
                {'from': twin.email, 'to': collab, 'type': 'collaboration'}
                for collab in twin.network_analysis.collaborators[:10]
            ]
        }
    
    def _generate_impact_visualization(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Генерация визуализации воздействия"""
        return {
            'overall_score': twin.impact_metrics.overall_impact_score,
            'breakdown': {
                'citation_impact': twin.impact_metrics.citation_impact.get('publication_count', 0),
                'research_visibility': twin.impact_metrics.research_impact.get('research_visibility', 0),
                'teaching_positions': twin.impact_metrics.teaching_impact.get('teaching_positions', 0),
                'industry_relevance': twin.impact_metrics.industry_impact.get('industry_relevance_score', 0),
                'social_engagement': twin.impact_metrics.social_impact.get('public_engagement_score', 0)
            }
        }
    
    def _generate_research_cloud(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Генерация облака исследовательских областей"""
        research_areas = twin.academic_profile.get('research_areas', [])
        
        return {
            'words': [
                {'text': area, 'size': 20 + len(area)}
                for area in research_areas
            ]
        }
    
    def _generate_collaboration_network(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Генерация сети коллабораций"""
        return {
            'centrality_score': twin.network_analysis.centrality_score,
            'network_size': twin.network_analysis.network_size,
            'influence_score': twin.network_analysis.influence_score,
            'key_collaborators': twin.network_analysis.collaborators[:5]
        }
    
    def _generate_publication_trends(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Генерация трендов публикаций"""
        publications = twin.academic_profile.get('publications', [])
        
        # Группируем по годам
        years = {}
        for pub in publications:
            year = pub.get('year')
            if year and year.isdigit():
                years[year] = years.get(year, 0) + 1
        
        return {
            'yearly_counts': sorted([
                {'year': year, 'count': count}
                for year, count in years.items()
            ], key=lambda x: x['year']),
            'total_publications': len(publications),
            'active_years': len(years)
        }

class DigitalTwinCreator:
    """Основной класс для создания цифрового двойника"""
    
    def __init__(self):
        self.personality_analyzer = PersonalityAnalyzer()
        self.network_analyzer = NetworkAnalyzer()
        self.career_analyzer = CareerAnalyzer()
        self.impact_analyzer = ImpactAnalyzer()
        self.visualization_generator = VisualizationDataGenerator()
    
    def create_digital_twin(self, email: str, academic_data: Dict[str, Any], 
                           search_results: List[Dict[str, Any]]) -> DigitalTwin:
        """Создание цифрового двойника"""
        logger.info(f"Creating digital twin for {email}")
        
        twin = DigitalTwin()
        twin.email = email
        twin.creation_timestamp = datetime.now().isoformat()
        
        # Основная информация
        academic_profile = academic_data.get('academic_profile', {})
        twin.academic_profile = academic_profile
        twin.name = academic_profile.get('name')
        
        # Определяем основную аффилиацию
        institutions = academic_profile.get('institutions', [])
        twin.primary_affiliation = institutions[0] if institutions else None
        
        # Анализ личности
        text_data = self._extract_text_data(search_results)
        twin.personality_profile = self.personality_analyzer.analyze_personality(
            text_data, academic_profile
        )
        
        # Сетевой анализ
        twin.network_analysis = self.network_analyzer.analyze_network(
            academic_profile, search_results
        )
        
        # Карьерный анализ
        twin.career_trajectory = self.career_analyzer.analyze_career(academic_profile)
        
        # Анализ воздействия
        twin.impact_metrics = self.impact_analyzer.analyze_impact(
            academic_profile, search_results
        )
        
        # Расчет показателей качества
        twin.confidence_score = self._calculate_confidence_score(academic_data, search_results)
        twin.completeness_score = self._calculate_completeness_score(twin)
        
        # Генерация данных для визуализации
        twin.visualization_data = self.visualization_generator.generate_visualization_data(twin)
        
        # Источники данных
        twin.data_sources = self._extract_data_sources(search_results)
        
        logger.info(f"Digital twin created for {email} with confidence {twin.confidence_score:.2f}")
        
        return twin
    
    def _extract_text_data(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """Извлечение текстовых данных для анализа"""
        text_data = []
        
        for result in search_results:
            text_data.append(result.get('title', ''))
            text_data.append(result.get('snippet', ''))
        
        return [text for text in text_data if text.strip()]
    
    def _calculate_confidence_score(self, academic_data: Dict[str, Any], 
                                   search_results: List[Dict[str, Any]]) -> float:
        """Расчет показателя уверенности"""
        confidence_scores = academic_data.get('confidence_scores', {})
        
        # Берем общую уверенность из академических данных
        base_confidence = confidence_scores.get('overall', 0.0)
        
        # Добавляем факторы из результатов поиска
        high_score_results = len([r for r in search_results if r.get('academic_score', 0) > 0.6])
        search_confidence = min(1.0, high_score_results / 5.0)
        
        # Комбинируем
        return (base_confidence + search_confidence) / 2.0
    
    def _calculate_completeness_score(self, twin: DigitalTwin) -> float:
        """Расчет показателя полноты данных"""
        score = 0.0
        total_fields = 10
        
        # Проверяем наличие ключевых данных
        if twin.name:
            score += 1
        if twin.academic_profile.get('degrees'):
            score += 1
        if twin.academic_profile.get('positions'):
            score += 1
        if twin.academic_profile.get('institutions'):
            score += 1
        if twin.academic_profile.get('publications'):
            score += 1
        if twin.academic_profile.get('research_areas'):
            score += 1
        if twin.network_analysis.collaborators:
            score += 1
        if twin.career_trajectory.career_milestones:
            score += 1
        if twin.impact_metrics.overall_impact_score > 0:
            score += 1
        if twin.academic_profile.get('academic_websites'):
            score += 1
        
        return score / total_fields
    
    def _extract_data_sources(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """Извлечение источников данных"""
        sources = set()
        
        for result in search_results:
            url = result.get('url', '')
            if url:
                # Извлекаем домен
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                    sources.add(domain)
                except:
                    pass
        
        return list(sources)
    
    def export_twin_to_json(self, twin: DigitalTwin) -> str:
        """Экспорт цифрового двойника в JSON"""
        return json.dumps(asdict(twin), indent=2, ensure_ascii=False)
    
    def generate_twin_summary(self, twin: DigitalTwin) -> Dict[str, Any]:
        """Генерация краткой сводки цифрового двойника"""
        return {
            'identity': {
                'name': twin.name or 'Unknown',
                'email': twin.email,
                'primary_affiliation': twin.primary_affiliation or 'Unknown'
            },
            'academic_status': {
                'career_stage': twin.personality_profile.career_stage,
                'expertise_level': twin.personality_profile.expertise_level,
                'academic_rank': twin.academic_profile.get('academic_rank'),
                'research_areas_count': len(twin.academic_profile.get('research_areas', []))
            },
            'impact_summary': {
                'overall_impact_score': twin.impact_metrics.overall_impact_score,
                'publication_count': len(twin.academic_profile.get('publications', [])),
                'network_size': twin.network_analysis.network_size,
                'digital_presence': twin.personality_profile.digital_presence
            },
            'quality_metrics': {
                'confidence_score': twin.confidence_score,
                'completeness_score': twin.completeness_score,
                'data_sources_count': len(twin.data_sources)
            },
            'visualization_ready': bool(twin.visualization_data)
        }

# Пример использования
async def main():
    from academic_intelligence import AcademicIntelligenceCollector
    
    # Сбор академических данных
    collector = AcademicIntelligenceCollector()
    academic_data = await collector.collect_academic_profile("john.smith@university.edu")
    
    # Создание цифрового двойника
    twin_creator = DigitalTwinCreator()
    digital_twin = twin_creator.create_digital_twin(
        "john.smith@university.edu",
        academic_data,
        academic_data.get('search_results', [])
    )
    
    # Вывод сводки
    summary = twin_creator.generate_twin_summary(digital_twin)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
