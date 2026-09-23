# OpenDataAnalysisTokouynu: Japanese Open Data Empirical Analysis & English Academic Paper Auto-Publisher

Autonomous GitHub Actions continuous pipeline that extracts official open datasets released by the Japanese government (MEXT, NIER, Statistics Bureau e-Stat, Digital Agency), performs rigorous statistical modeling (Descriptive, OLS Trend Regressions, Bivariate Correlations, Bayes Factors), synthesizes **peer-reviewed working papers in English (IMRaD format)** via Google Gemini AI / academic templates, compiles publication-ready figures & PDFs, and **automatically publishes 1 paper per day to WordPress** ([kouynu.wordpress.com](https://kouynu.wordpress.com/)).

---

## 🌟 Key Features

1. **Official Japanese Public Open Data**:
   - MEXT National Assessment of Academic Ability (Mathematics, affective motivation, digital usage).
   - MEXT Annual Survey on School Educational Informatization (1-to-1 devices, teacher ICT competencies).
   - MEXT School Basic Survey (STEM & Computer Science collegiate admissions, gender parity).
   - MEXT Teacher Working Conditions Survey (Workload, on-campus hours, club coaching overtime).
   - MEXT Student Guidance Survey (Absenteeism, bullying incidents, online attendance accreditation).
   - Upper Secondary Informatics Curriculum ("Information I", Python vs JavaScript adoption).
   - International Comparative Datasets (OECD PISA, OECD TALIS, IEA TIMSS, UNESCO, World Bank).

2. **Empirical Quantitative Statistical Modeling (`src/analyzer.py`)**:
   - Parametric descriptive statistics: Mean, Median, Standard Deviation, Interquartile Range (IQR), Skewness.
   - Ordinary Least Squares (OLS) longitudinal trend estimation: Slope ($\beta$), Intercept ($\alpha$), Coefficient of determination ($R^2$), two-tailed $p$-values, CAGR.
   - Bivariate correlation modeling: Pearson $r$, $R^2$, significance levels, qualitative effect size interpretations.
   - Bayesian Evidence: Approximation of Bayes Factors ($BF_{10}$) for model strength.
   - Inter-group disparity metrics: Maximum-minimum gap ratios, subgroup comparisons.

3. **Publication-Ready Figures in English (`src/visualizer.py`)**:
   - 200–300 DPI high-resolution scientific charts rendered in Seaborn/Matplotlib.
   - Trend trajectories across educational tiers and correlation scatter plots with fitted OLS lines.
   - Clean academic styling (Academic Navy, Slate, Emerald) with zero non-Latin font clipping.

4. **Peer-Reviewed English Academic Papers (`src/academic_paper_en.py`)**:
   - Adheres strictly to international journal IMRaD standards:
     - **Title & Abstract**: 200–250 words structured abstract with parametric statistics + 5–6 academic keywords.
     - **1. Introduction & Background**: Societal and policy context in Japan (GIGA School Project, curriculum guidelines).
     - **2. Theoretical Framework & Hypotheses**: Operationalized research questions (RQ1, RQ2) and testable hypotheses (H1, H2).
     - **3. Methodology & Dataset**: Official data provenance, sample scope, statistical techniques.
     - **4. Empirical Results**: Rigorous parametric narrative citing exact regression metrics and correlations.
     - **5. Discussion & Policy Implications**: Theoretical alignment, administrative implications for Japanese and international education.
     - **6. Limitations & Future Directions**: Ecological fallacy cautions, panel data recommendations.
     - **7. References**: APA 7th edition standard academic bibliography.

5. **Formal Synthetic Peer Review Assessment (`src/peer_review_en.py`)**:
   - Reviewer 1 (Quantitative Modeling) & Reviewer 2 (Educational Policy) evaluations with an editorial synthesis decision (*"Accept with Minor Revision"*).

6. **Full-Featured WordPress Publishing (`src/publishers/`)**:
   - **WordPress REST API** (Recommended): Uploads media figures to WP Media Library, sets featured image, creates categories, and publishes responsive HTML posts with Booktabs statistical tables.
   - **WordPress Post by Email** (SMTP): Email fallback with attached figures and PDFs.
   - **Local Markdown & PDF Persistence**: Stored under `reports/` with automatic GitHub repository commits.

7. **Daily Rotation & Continuous Archiving (`src/storage.py`)**:
   - 1 paper generated and published every single day via GitHub Actions schedule (`0 21 * * *` UTC = 06:00 JST).
   - Synchronizes machine-readable `data/posted_papers.json` and human-readable `data/PAPERS_ARCHIVE.md`.

---

## 📂 Directory Structure

```
OpenDataAnalysisTokouynu/
├── .github/
│   └── workflows/
│       └── daily_english_paper.yml   # Daily scheduled run (06:00 JST / 21:00 UTC) & dispatch
├── src/
│   ├── __init__.py
│   ├── config.py                     # Configuration loader & constants
│   ├── analyzer.py                   # Quantitative statistical analysis engine
│   ├── visualizer.py                 # 300-DPI English figure rendering
│   ├── academic_contexts_en.py       # English literature contexts & APA citations
│   ├── academic_paper_en.py          # English academic paper generator (IMRaD)
│   ├── peer_review_en.py             # English peer review report generator
│   ├── reporter.py                   # WordPress HTML & Markdown builder
│   ├── storage.py                    # History JSON & PAPERS_ARCHIVE.md synchronization
│   ├── main.py                       # CLI pipeline entry point
│   ├── fetchers/                     # Data catalog models & daily rotation
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── catalog.py
│   ├── pdf/                          # PDF generator
│   │   ├── __init__.py
│   │   └── pdf_generator_en.py
│   └── publishers/                   # Multi-target publishers
│       ├── __init__.py
│       ├── base.py
│       ├── wordpress_rest.py         # WP REST API with media upload
│       ├── wordpress_mail.py         # Post by Email via SMTP
│       └── markdown_file.py          # Local repository reports/
├── data/
│   ├── catalog/                      # Master datasets in English (JSON)
│   ├── posted_papers.json            # Machine history of published topics
│   └── PAPERS_ARCHIVE.md             # Public table of published papers
├── reports/                          # Generated markdown, figures, and PDFs
├── tests/                            # Pytest test suite
├── tools/                            # Utility & enrichment scripts
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Setup & Deployment Guide

### Step 1: Clone or Push Repository to GitHub
Ensure the repository is pushed to your GitHub account (e.g. `k518-2026/OpenDataAnalysisTokouynu`).

### Step 2: Configure GitHub Repository Permissions
To allow GitHub Actions to commit the generated reports and history files back to the repository:
1. Go to repository **Settings** -> **Actions** -> **General**.
2. Under **Workflow permissions**, select **"Read and write permissions"**.
3. Click **Save**.

### Step 3: Configure GitHub Actions Secrets
In your GitHub repository, navigate to **Settings** -> **Secrets and variables** -> **Actions** and add:

| Secret Name | Required | Description |
| :--- | :---: | :--- |
| `GEMINI_API_KEY` | Recommended | Google AI Studio API key for Gemini 2.5 Flash synthesis |
| `WP_SITE_URL` | **Yes** | Your WordPress site URL (e.g., `https://kouynu.wordpress.com`) |
| `WP_USER` | **Yes** | WordPress admin username |
| `WP_APP_PASSWORD` | **Yes** | WordPress Application Password (Users -> Profile -> Application Passwords) |
| `WP_POST_EMAIL` | Optional | WordPress Post by Email secret address (if using email publisher) |
| `SMTP_USER` | Optional | Sender email address (if using email publisher) |
| `SMTP_PASS` | Optional | Sender email app password (if using email publisher) |

*(Note: If `GEMINI_API_KEY` is omitted, the system seamlessly uses the built-in deterministic academic template engine with zero quota cost).*

---

## 💻 Local CLI Execution

Run simulation (dry-run):
```bash
python -m src.main --dry-run
```

Run specific dataset and angle:
```bash
python -m src.main --dataset japan_national_assessment_math --angle math_affective_gap --dry-run
```

Run test suite:
```bash
pytest tests/
```
