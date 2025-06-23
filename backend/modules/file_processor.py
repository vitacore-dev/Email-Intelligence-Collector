import csv
import io
import re
import asyncio
from typing import List, Dict, Any
from fastapi import UploadFile
import logging

from .data_collector import DataCollector
from .email_validator import EmailValidator

logger = logging.getLogger(__name__)

class FileProcessor:
    """Класс для обработки файлов с email-адресами"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.supported_formats = ['.csv', '.txt']
    
    async def process_file(self, file: UploadFile) -> Dict[str, Any]:
        """Обработка загруженного файла"""
        logger.info(f"Processing file: {file.filename}")
        
        # Проверка формата файла
        if not any(file.filename.lower().endswith(fmt) for fmt in self.supported_formats):
            raise ValueError(f"Unsupported file format. Supported: {', '.join(self.supported_formats)}")
        
        # Чтение содержимого файла
        content = await file.read()
        text_content = content.decode('utf-8', errors='ignore')
        
        # Извлечение email-адресов
        emails = self._extract_emails_from_content(text_content, file.filename)
        
        # Инициализация результатов
        results = {
            'total': len(emails),
            'processed': 0,
            'existing': 0,
            'new': 0,
            'invalid': 0,
            'results': []
        }
        
        # Обработка каждого email
        for email in emails:
            try:
                result = await self._process_single_email(email)
                results['results'].append(result)
                
                if result['status'] == 'invalid':
                    results['invalid'] += 1
                elif result['status'] == 'from_cache':
                    results['existing'] += 1
                elif result['status'] == 'new':
                    results['new'] += 1
                
                results['processed'] += 1
                
            except Exception as e:
                logger.error(f"Error processing email {email}: {e}")
                results['results'].append({
                    'email': email,
                    'status': 'error',
                    'error': str(e),
                    'data': None
                })
        
        logger.info(f"File processing completed. Processed: {results['processed']}/{results['total']}")
        return results
    
    def _extract_emails_from_content(self, content: str, filename: str) -> List[str]:
        """Извлечение email-адресов из содержимого файла"""
        emails = set()
        
        try:
            if filename.lower().endswith('.csv'):
                # Обработка CSV файла
                emails.update(self._extract_from_csv(content))
            else:
                # Обработка текстового файла
                emails.update(self._extract_from_text(content))
        
        except Exception as e:
            logger.error(f"Error extracting emails from {filename}: {e}")
            # Fallback: поиск email в тексте
            emails.update(EmailValidator.extract_emails_from_text(content))
        
        return list(emails)
    
    def _extract_from_csv(self, content: str) -> List[str]:
        """Извлечение email из CSV файла"""
        emails = set()
        
        try:
            # Попробуем разные разделители
            for delimiter in [',', ';', '\t']:
                try:
                    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
                    for row in reader:
                        for cell in row:
                            if cell and '@' in cell:
                                found_emails = EmailValidator.extract_emails_from_text(cell)
                                emails.update(found_emails)
                    
                    # Если нашли email с этим разделителем, используем его
                    if emails:
                        break
                        
                except Exception:
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
        
        return list(emails)
    
    def _extract_from_text(self, content: str) -> List[str]:
        """Извлечение email из текстового файла"""
        # Разбиваем по строкам и ищем email в каждой
        emails = set()
        
        for line in content.split('\n'):
            line = line.strip()
            if line:
                # Проверяем, является ли строка email
                if EmailValidator.is_valid(line):
                    emails.add(line.lower())
                else:
                    # Ищем email в строке
                    found_emails = EmailValidator.extract_emails_from_text(line)
                    emails.update(found_emails)
        
        return list(emails)
    
    async def _process_single_email(self, email: str) -> Dict[str, Any]:
        """Обработка одного email-адреса"""
        # Валидация email
        if not EmailValidator.is_valid(email):
            return {
                'email': email,
                'status': 'invalid',
                'error': 'Invalid email format',
                'data': None
            }
        
        email = email.lower().strip()
        
        # Проверка в базе данных
        from database.models import EmailProfile
        existing_profile = self.db.query(EmailProfile).filter(
            EmailProfile.email == email
        ).first()
        
        if existing_profile:
            return {
                'email': email,
                'status': 'from_cache',
                'data': existing_profile.to_dict()
            }
        
        # Сбор новых данных
        try:
            collector = DataCollector(email)
            profile_data = await collector.collect_all()
            
            # Сохранение в базу данных
            profile = EmailProfile(
                email=email,
                data=profile_data,
                source_count=len(profile_data.get('sources', []))
            )
            
            self.db.merge(profile)
            self.db.commit()
            
            return {
                'email': email,
                'status': 'new',
                'data': profile_data
            }
            
        except Exception as e:
            logger.error(f"Error collecting data for {email}: {e}")
            return {
                'email': email,
                'status': 'error',
                'error': str(e),
                'data': None
            }
    
    def validate_file_size(self, file: UploadFile, max_size_mb: int = 10) -> bool:
        """Проверка размера файла"""
        if hasattr(file, 'size') and file.size:
            return file.size <= max_size_mb * 1024 * 1024
        return True  # Если размер неизвестен, разрешаем
    
    def get_file_stats(self, content: str, filename: str) -> Dict[str, Any]:
        """Получение статистики файла"""
        emails = self._extract_emails_from_content(content, filename)
        
        stats = {
            'filename': filename,
            'total_emails': len(emails),
            'unique_domains': len(set(email.split('@')[1] for email in emails if '@' in email)),
            'file_size': len(content.encode('utf-8')),
            'preview_emails': emails[:5]  # Первые 5 email для предпросмотра
        }
        
        return stats

