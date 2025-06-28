#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PyPDF2
import pdfplumber
import re
import sys
from pathlib import Path

def extract_text_pypdf2(pdf_path):
    """Извлечение текста с помощью PyPDF2"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            print(f"Количество страниц в PDF: {len(reader.pages)}")
            
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += f"\n=== СТРАНИЦА {i+1} ===\n"
                text += page_text
                
    except Exception as e:
        print(f"Ошибка PyPDF2: {e}")
    
    return text

def extract_text_pdfplumber(pdf_path):
    """Извлечение текста с помощью pdfplumber (более точный)"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Количество страниц в PDF: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n=== СТРАНИЦА {i+1} ===\n"
                    text += page_text
                
    except Exception as e:
        print(f"Ошибка pdfplumber: {e}")
    
    return text

def find_email_context(text, target_email):
    """Поиск контекста вокруг целевого email"""
    lines = text.split('\n')
    results = []
    
    for i, line in enumerate(lines):
        if target_email.lower() in line.lower():
            # Контекст: 3 строки до и 3 строки после
            start = max(0, i-3)
            end = min(len(lines), i+4)
            
            context = {
                'line_number': i+1,
                'line': line,
                'context': lines[start:end],
                'context_range': f"строки {start+1}-{end}"
            }
            results.append(context)
    
    return results

def extract_authors_and_contacts(text):
    """Извлечение информации об авторах и контактах"""
    # Поиск паттернов авторов
    author_patterns = [
        r'[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+',  # ФИО на русском
        r'[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+',  # ФИО на английском
        r'[А-ЯЁ]\.?\s*[А-ЯЁ]\.?\s*[А-ЯЁ][а-яё]+',  # Инициалы + фамилия
    ]
    
    # Поиск email адресов
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Поиск телефонов
    phone_patterns = [
        r'\+7\s*\(\d{3}\)\s*\d{3}-\d{2}-\d{2}',
        r'\+7\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}',
        r'8\s*\(\d{3}\)\s*\d{3}-\d{2}-\d{2}',
    ]
    
    authors = []
    emails = []
    phones = []
    
    # Поиск авторов
    for pattern in author_patterns:
        matches = re.findall(pattern, text)
        authors.extend(matches)
    
    # Поиск email адресов
    emails = re.findall(email_pattern, text)
    
    # Поиск телефонов
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phones.extend(matches)
    
    return {
        'authors': list(set(authors)),
        'emails': list(set(emails)),
        'phones': list(set(phones))
    }

def extract_affiliations(text):
    """Извлечение информации об аффилиации (учреждения, адреса)"""
    # Поиск учреждений
    institution_patterns = [
        r'[А-ЯЁ][а-яё]*\s+[а-яё]*\s*[Уу]ниверситет',
        r'[А-ЯЁ][а-яё]*\s+[а-яё]*\s*[Ии]нститут',
        r'[А-ЯЁ][а-яё]*\s+[а-яё]*\s*[Цц]ентр',
        r'[А-ЯЁ][а-яё]*\s+[а-яё]*\s*[Кк]линика',
        r'[А-ЯЁ][а-яё]*\s+[а-яё]*\s*[Аа]кадеми[яи]',
    ]
    
    # Поиск адресов
    address_patterns = [
        r'г\.\s*[А-ЯЁ][а-яё]+',
        r'[А-ЯЁ][а-яё]+,\s*\d+',
        r'ул\.\s*[А-ЯЁ][а-яё\s]+,\s*\d+',
    ]
    
    institutions = []
    addresses = []
    
    for pattern in institution_patterns:
        matches = re.findall(pattern, text)
        institutions.extend(matches)
    
    for pattern in address_patterns:
        matches = re.findall(pattern, text)
        addresses.extend(matches)
    
    return {
        'institutions': list(set(institutions)),
        'addresses': list(set(addresses))
    }

def analyze_pdf(pdf_path, target_email):
    """Основная функция анализа PDF"""
    print(f"Анализ PDF документа: {pdf_path}")
    print(f"Поиск email: {target_email}")
    print("=" * 60)
    
    # Извлечение текста двумя способами
    print("1. Извлечение текста с помощью PyPDF2...")
    text_pypdf2 = extract_text_pypdf2(pdf_path)
    
    print("\n2. Извлечение текста с помощью pdfplumber...")
    text_pdfplumber = extract_text_pdfplumber(pdf_path)
    
    # Выбираем лучший результат
    text = text_pdfplumber if len(text_pdfplumber) > len(text_pypdf2) else text_pypdf2
    
    print(f"\nИзвлечено символов: {len(text)}")
    
    # Поиск целевого email
    print(f"\n3. Поиск email '{target_email}'...")
    email_contexts = find_email_context(text, target_email)
    
    if email_contexts:
        print(f"✅ Email найден в {len(email_contexts)} местах!")
        for i, context in enumerate(email_contexts):
            print(f"\n--- Вхождение {i+1} ---")
            print(f"Строка {context['line_number']}: {context['line']}")
            print(f"Контекст ({context['context_range']}):")
            for line in context['context']:
                print(f"  {line}")
    else:
        print("❌ Email не найден в извлеченном тексте")
    
    # Анализ авторов и контактов
    print("\n4. Анализ авторов и контактной информации...")
    contacts = extract_authors_and_contacts(text)
    
    print(f"Найдено авторов: {len(contacts['authors'])}")
    for author in contacts['authors'][:10]:  # Показываем первых 10
        print(f"  - {author}")
    
    print(f"\nНайдено email адресов: {len(contacts['emails'])}")
    for email in contacts['emails']:
        print(f"  - {email}")
    
    print(f"\nНайдено телефонов: {len(contacts['phones'])}")
    for phone in contacts['phones']:
        print(f"  - {phone}")
    
    # Анализ аффилиации
    print("\n5. Анализ учреждений и адресов...")
    affiliations = extract_affiliations(text)
    
    print(f"Найдено учреждений: {len(affiliations['institutions'])}")
    for inst in affiliations['institutions']:
        print(f"  - {inst}")
    
    print(f"\nНайдено адресов: {len(affiliations['addresses'])}")
    for addr in affiliations['addresses']:
        print(f"  - {addr}")
    
    # Сохранение полного текста для дальнейшего анализа
    output_file = "/tmp/extracted_text.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"\n📄 Полный текст сохранен в: {output_file}")
    
    return {
        'text': text,
        'email_contexts': email_contexts,
        'contacts': contacts,
        'affiliations': affiliations
    }

if __name__ == "__main__":
    pdf_path = "/tmp/found_pdf.pdf"
    target_email = "buch1202@mail.ru"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF файл не найден: {pdf_path}")
        sys.exit(1)
    
    results = analyze_pdf(pdf_path, target_email)
