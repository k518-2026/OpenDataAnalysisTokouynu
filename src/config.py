"""
Configuration settings for OpenDataAnalysisTokouynu.
"""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TEMP_DIR = BASE_DIR / "temp"
REPORTS_DIR = BASE_DIR / "reports"
PDF_REPORTS_DIR = REPORTS_DIR / "pdf"
CATALOG_DIR = DATA_DIR / "catalog"

# Ensure runtime directories exist
DATA_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
PDF_REPORTS_DIR.mkdir(exist_ok=True)
CATALOG_DIR.mkdir(exist_ok=True)


class Config:
    """System configuration loaded from environment variables."""

    # Google Gemini AI settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_TEXT_MODEL: str = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash").strip()

    # Anthropic Claude AI settings
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "").strip()
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest").strip()

    # Blog publishing mode: 'wordpress_rest', 'wordpress_mail', or 'markdown_only'
    BLOG_PUBLISHER_TYPE: str = os.getenv("BLOG_PUBLISHER_TYPE", "wordpress_rest").strip().lower()

    # WordPress REST API settings
    WP_SITE_URL: str = os.getenv("WP_SITE_URL", "https://kouynu.wordpress.com").strip().rstrip("/")
    WP_USER: str = os.getenv("WP_USER", "").strip()
    WP_APP_PASSWORD: str = os.getenv("WP_APP_PASSWORD", "").replace(" ", "").strip()
    WP_POST_STATUS: str = os.getenv("WP_POST_STATUS", "publish").strip()
    DEFAULT_CATEGORIES: str = os.getenv(
        "DEFAULT_CATEGORIES", "Open Data Analysis,Educational Policy,Empirical Research"
    ).strip()

    # WordPress Post by Email settings (SMTP fallback)
    WP_POST_EMAIL: str = os.getenv("WP_POST_EMAIL", "").strip()
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "").strip()
    SMTP_PASS: str = os.getenv("SMTP_PASS", "").replace(" ", "").strip()

    # Defaults
    DEFAULT_TOPIC: str = os.getenv("DEFAULT_TOPIC", "all").strip().lower()

    # GitHub Repository settings
    GITHUB_REPOSITORY: str = os.getenv("GITHUB_REPOSITORY", "k518-2026/OpenDataAnalysisTokouynu").strip()
    GITHUB_BRANCH: str = os.getenv("GITHUB_BRANCH", "main").strip()

    # Storage paths
    POSTED_PAPERS_PATH = DATA_DIR / "posted_papers.json"
    PAPERS_ARCHIVE_PATH = DATA_DIR / "PAPERS_ARCHIVE.md"
    PDF_ARCHIVE_DIR = PDF_REPORTS_DIR
