import re
import dns.resolver
import socket
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class EmailValidator:
    """Класс для валидации email-адресов"""
    
    # Регулярное выражение для базовой проверки email
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # Список одноразовых email доменов
    DISPOSABLE_DOMAINS = {
        '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
        'mailinator.com', 'yopmail.com', 'temp-mail.org'
    }
    
    @classmethod
    def is_valid(cls, email: str) -> bool:
        """Базовая проверка формата email"""
        if not email or not isinstance(email, str):
            return False
        
        email = email.strip().lower()
        return bool(cls.EMAIL_REGEX.match(email))
    
    @classmethod
    def validate_comprehensive(cls, email: str) -> Dict[str, any]:
        """Комплексная валидация email с проверкой домена"""
        result = {
            'email': email,
            'is_valid': False,
            'format_valid': False,
            'domain_exists': False,
            'mx_record_exists': False,
            'is_disposable': False,
            'domain_info': {},
            'errors': []
        }
        
        try:
            email = email.strip().lower()
            
            # Проверка формата
            if not cls.is_valid(email):
                result['errors'].append('Invalid email format')
                return result
            
            result['format_valid'] = True
            
            # Извлечение домена
            domain = email.split('@')[1]
            
            # Проверка на одноразовый email
            if domain in cls.DISPOSABLE_DOMAINS:
                result['is_disposable'] = True
                result['errors'].append('Disposable email domain')
            
            # Проверка существования домена
            domain_exists, mx_exists, domain_info = cls._check_domain(domain)
            
            result['domain_exists'] = domain_exists
            result['mx_record_exists'] = mx_exists
            result['domain_info'] = domain_info
            
            if not domain_exists:
                result['errors'].append('Domain does not exist')
            
            if not mx_exists:
                result['errors'].append('No MX record found')
            
            # Общая валидность
            result['is_valid'] = (
                result['format_valid'] and 
                result['domain_exists'] and 
                result['mx_record_exists'] and 
                not result['is_disposable']
            )
            
        except Exception as e:
            logger.error(f"Error validating email {email}: {e}")
            result['errors'].append(f'Validation error: {str(e)}')
        
        return result
    
    @classmethod
    def _check_domain(cls, domain: str) -> Tuple[bool, bool, Dict]:
        """Проверка домена и MX записей"""
        domain_info = {}
        domain_exists = False
        mx_exists = False
        
        try:
            # Проверка A записи (существование домена)
            try:
                a_records = dns.resolver.resolve(domain, 'A')
                domain_exists = True
                domain_info['a_records'] = [str(record) for record in a_records]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                pass
            
            # Проверка MX записи
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                mx_exists = True
                domain_info['mx_records'] = [
                    {'priority': record.preference, 'exchange': str(record.exchange)}
                    for record in mx_records
                ]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                pass
            
            # Дополнительная информация о домене
            try:
                # TXT записи (могут содержать SPF, DKIM и другую информацию)
                txt_records = dns.resolver.resolve(domain, 'TXT')
                domain_info['txt_records'] = [str(record) for record in txt_records]
            except:
                pass
            
        except Exception as e:
            logger.error(f"Error checking domain {domain}: {e}")
        
        return domain_exists, mx_exists, domain_info
    
    @classmethod
    def extract_emails_from_text(cls, text: str) -> list:
        """Извлечение всех email-адресов из текста"""
        if not text:
            return []
        
        # Расширенное регулярное выражение для поиска email в тексте
        email_pattern = re.compile(
            r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        )
        
        emails = email_pattern.findall(text)
        
        # Фильтрация и валидация найденных email
        valid_emails = []
        for email in emails:
            email = email.lower().strip()
            if cls.is_valid(email):
                valid_emails.append(email)
        
        return list(set(valid_emails))  # Убираем дубликаты
    
    @classmethod
    def get_domain_reputation(cls, domain: str) -> Dict[str, any]:
        """Получение информации о репутации домена"""
        reputation = {
            'domain': domain,
            'is_business': False,
            'is_educational': False,
            'is_government': False,
            'is_popular_provider': False,
            'provider_type': 'unknown'
        }
        
        # Популярные email провайдеры
        popular_providers = {
            'gmail.com': 'Google',
            'yahoo.com': 'Yahoo',
            'outlook.com': 'Microsoft',
            'hotmail.com': 'Microsoft',
            'icloud.com': 'Apple',
            'aol.com': 'AOL',
            'mail.ru': 'Mail.Ru',
            'yandex.ru': 'Yandex'
        }
        
        # Образовательные домены
        educational_tlds = {'.edu', '.ac.uk', '.edu.au', '.edu.cn'}
        
        # Правительственные домены
        government_tlds = {'.gov', '.gov.uk', '.gov.au', '.gov.cn'}
        
        domain_lower = domain.lower()
        
        if domain_lower in popular_providers:
            reputation['is_popular_provider'] = True
            reputation['provider_type'] = popular_providers[domain_lower]
        
        # Проверка на образовательные домены
        for tld in educational_tlds:
            if domain_lower.endswith(tld):
                reputation['is_educational'] = True
                reputation['provider_type'] = 'Educational'
                break
        
        # Проверка на правительственные домены
        for tld in government_tlds:
            if domain_lower.endswith(tld):
                reputation['is_government'] = True
                reputation['provider_type'] = 'Government'
                break
        
        # Если не популярный провайдер и не специальный домен, вероятно бизнес
        if (not reputation['is_popular_provider'] and 
            not reputation['is_educational'] and 
            not reputation['is_government']):
            reputation['is_business'] = True
            reputation['provider_type'] = 'Business'
        
        return reputation

