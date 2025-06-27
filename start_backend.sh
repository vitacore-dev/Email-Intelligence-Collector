#!/bin/bash
cd /Users/rafaelamirov/Documents/metod/Email-Intelligence-Collector/backend
source venv/bin/activate
export PYTHONPATH=/Users/rafaelamirov/Documents/metod/Email-Intelligence-Collector/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
