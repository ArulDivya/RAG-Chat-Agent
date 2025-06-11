**Federal Documents Query System**
**Table of Contents**

Introduction

Features

Installation

Usage

Project Structure

Contact

**Introduction**
FederalDocQA is an offline Retrieval-Augmented Generation (RAG) system that transforms how you interact with federal documents. By combining local Ollama LLMs with a structured MySQL database, it delivers accurate, source-cited answers to complex policy questions without requiring internet access or cloud APIs. The system features an automated daily update pipeline to ensure document freshness, wrapped in a privacy-first architecture where all processing occurs on-device. With its FastAPI backend, researchers, journalists, and engaged citizens can effortlessly query thousands of regulations on topics like climate change, AI governance, and healthcare – getting instant summaries with traceable references.

**Key aspects:**

Local LLM Integration: Uses Ollama with qwen2 model (no OpenAI dependencies)

Database Backend: MySQL for storing federal documents

Modern Stack: FastAPI backend 

Accuracy Focus: Combines direct database queries with LLM summarization

**Features**
Feature	Description
Document Retrieval	SQL queries to MySQL database
AI Summarization	Local qwen2 model via Ollama
Web Interface	Interactive query builder
Daily Updates	Automated data pipeline
**Installation**
1. Prerequisites
Python 3.10+

MySQL 8.0+

Ollama (for local LLM)

2. Setup
bash
# Clone repository
git clone https://github.com/yourrepo/federal-documents-rag.git
cd federal-documents-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
mysql -u root -p < federal.sql
3. Configure Environment
Create .env file:

**Usage**
1. Start Services
bash
# Terminal 1 - LLM
ollama serve

# Terminal 2 - Backend
uvicorn app:app --reload

# Terminal 3 - Frontend
streamlit run web_app.py
2. Access Interfaces
Component	URL
API Docs	http://localhost:8000/docs
Web App	http://localhost:8501

**Project Structure**
text
federal-documents-rag/
├── data/
│   ├── pipeline/         
│   └── samples/           
├── app/
│   ├── api/               
│   ├── core/              
│   └── llm/               
├── web_app.py             
├── app.py                
├── data_pipeline.py       
└── requirements.txt
**Contact**
Divyabarathi

Email: bharathi.divya87@gmail.com

