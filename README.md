# 🏦 BankWise AI

### AI-Powered Banking Marketing Intelligence Platform

> An end-to-end AI and machine-learning platform for **customer segmentation, personalized banking product recommendations, AI campaign generation, creative generation, compliance validation, campaign delivery, analytics, and governance**.

---

## 📌 Overview

**BankWise AI** is a banking marketing intelligence platform that combines **Machine Learning, Generative AI, and marketing automation** into a unified workflow.

The platform transforms customer and campaign data into actionable marketing intelligence:

```text
Customer Data
      ↓
Feature Engineering
      ↓
Customer Segmentation
      ↓
Customer Personas
      ↓
Product Recommendation
      ↓
Explainable Recommendation
      ↓
AI Campaign Generation
      ↓
Creative Generation
      ↓
Compliance Validation
      ↓
Human Approval
      ↓
Campaign Delivery
      ↓
Analytics & Governance
```

The project demonstrates how an AI-assisted marketing workflow can be designed with **personalization, explainability, compliance checkpoints, human oversight, and auditability**.

---

# 🎯 Project Objectives

BankWise AI was developed to address common challenges in banking marketing:

* Identifying meaningful customer segments
* Understanding customer behavior
* Matching customers with relevant banking products
* Explaining why a product was recommended
* Generating personalized campaign content
* Creating marketing creatives automatically
* Validating campaigns before delivery
* Supporting multiple communication channels
* Tracking campaign performance
* Maintaining audit and governance records

---

# ✨ Key Features

| Module             | Description                                                                            |
| ------------------ | -------------------------------------------------------------------------------------- |
| 📊 Dashboard       | Executive overview of customers, segments, recommendations, campaigns, and performance |
| 👤 Customer 360°   | Detailed customer profiles and behavioral information                                  |
| 🧩 Segmentation    | ML-based customer clustering and persona creation                                      |
| 🎯 Recommendations | Personalized banking product recommendations                                           |
| 🔍 Explainability  | Rationale behind customer-product recommendations                                      |
| ✍️ Campaign Studio | AI-generated personalized campaign content                                             |
| 🌐 Multilingual AI | Campaign generation in English, Hindi, and Marathi                                     |
| 🎨 Creative Studio | Automated marketing banner generation                                                  |
| 🛡️ Compliance     | Automated campaign compliance validation                                               |
| 👨‍💼 Approval     | Human-in-the-loop campaign approval                                                    |
| 📧 Delivery        | Email campaign delivery and SMS simulation                                             |
| 🧪 A/B Testing     | Generation and analysis of campaign variants                                           |
| 📈 Analytics       | Campaign and conversion analytics                                                      |
| 🗄️ Governance     | Audit logs and campaign history                                                        |

---

# 🏗️ System Architecture

```text
                         ┌───────────────────────┐
                         │      React Frontend   │
                         │   Vite + TypeScript   │
                         │ Tailwind + Recharts   │
                         └───────────┬───────────┘
                                     │
                                REST APIs
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │     FastAPI Backend   │
                         │       Python 3.10+    │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
     ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
     │ ML / Analytics │    │ Generative AI  │    │ Creative Engine│
     │                │    │                │    │                │
     │ Segmentation   │    │ Google Gemini  │    │ Python + PIL   │
     │ Recommendation │    │ Campaign Copy  │    │ Banner Engine  │
     │ Analytics      │    │ A/B Variants   │    │                │
     └────────────────┘    └────────────────┘    └────────────────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     ▼
                         ┌───────────────────────┐
                         │ SQLite / Audit Layer │
                         │ Campaign Records     │
                         │ Compliance Records   │
                         └───────────────────────┘
```

---

# 🔄 End-to-End Workflow

## 1. Customer Data

The platform works with customer, transaction, product, campaign, and interaction data.

Example customer attributes include:

* Income
* Account balance
* Credit profile
* Tenure
* Product holdings
* Transaction behavior
* Campaign engagement
* Digital engagement

---

## 2. Feature Engineering

Raw customer information is transformed into analytical features suitable for segmentation and recommendation.

The feature engineering layer prepares behavioral and financial indicators that can be used by downstream ML components.

```text
Raw Data
   ↓
Data Validation
   ↓
Data Cleaning
   ↓
Feature Engineering
   ↓
Customer Feature Dataset
```

---

# 🧩 3. Customer Segmentation

BankWise AI groups customers with similar behavioral and financial characteristics.

The segmentation workflow includes:

```text
Customer Features
       ↓
Preprocessing
       ↓
Feature Scaling
       ↓
Dimensionality Reduction / PCA
       ↓
Clustering
       ↓
Cluster Evaluation
       ↓
Cluster Profiling
       ↓
Customer Personas
```

### K-Means Clustering

K-Means is used to identify groups of customers with similar feature patterns.

The algorithm iteratively:

1. Initializes cluster centroids
2. Assigns customers to the nearest centroid
3. Recalculates centroids
4. Repeats until the clusters stabilize

### PCA

Principal Component Analysis is used as a dimensionality-reduction technique.

It helps:

* Reduce the number of dimensions
* Remove correlated information
* Improve visualization
* Analyze the structure of customer groups

### Cluster Evaluation

Cluster quality is evaluated using metrics such as:

* Silhouette Score
* Cluster size
* Cluster profiles
* Comparative evaluation across configurations

---

# 👥 4. Customer Personas

After clustering, each cluster is profiled using its characteristic customer attributes.

A persona represents the **typical characteristics of customers within a segment**.

For example, a segment may contain customers characterized by combinations of:

* Higher or lower income
* Higher or lower balances
* Different engagement levels
* Different product ownership
* Different transaction activity
* Different tenure patterns

The personas are then used as additional context for marketing decisions.

---

# 🎯 5. Product Recommendation Engine

The recommendation engine determines which banking products are relevant to individual customers.

The recommendation pipeline is:

```text
Customer Data
      ↓
Eligibility Filtering
      ↓
Customer-Product Scoring
      ↓
Recommendation Selection
      ↓
Recommendation Validation
      ↓
Final Recommendations
```

### Eligibility

Products are first evaluated against customer eligibility and business rules.

### Product Scoring

Eligible customer-product combinations receive a relevance score based on customer characteristics and product-related signals.

### Recommendation Output

The final recommendation dataset contains customer-product relationships that can be consumed by the campaign layer.

---

# 🔍 6. Explainable Recommendations

BankWise AI does not only surface a recommended product.

It also provides supporting rationale so marketers can understand the recommendation.

Example:

```text
Recommended Product:
Premium Savings Account

Reason:
Customer demonstrates strong balance levels,
high engagement, and characteristics aligned
with the product's target profile.
```

This provides greater transparency than presenting only a recommendation score.

---

# ✍️ 7. AI Campaign Studio

The Campaign Studio converts customer intelligence into personalized marketing content.

```text
Customer Profile
       +
Customer Segment
       +
Recommended Product
       +
Campaign Objective
       +
Language
       ↓
   Google Gemini
       ↓
Personalized Campaign
       ↓
A/B Variants
```

### Supported Languages

* English
* Hindi
* Marathi

### Campaign Capabilities

* Personalized messaging
* Product-specific content
* Customer-context-aware copy
* Multilingual generation
* A/B campaign variants

---

# 🎨 8. Creative Studio

The Creative Studio generates marketing banner graphics using a local Python/Pillow-based creative engine.

Capabilities include:

* Automated banner creation
* Multiple creative variations
* 1200 × 675 banner output
* Creative regeneration
* Creative provenance tracking

The creative generation layer is intentionally separated from the text-generation layer.

```text
Campaign Content
      ↓
Creative Parameters
      ↓
PIL Creative Engine
      ↓
Marketing Banner
      ↓
Creative Record
```

---

# 🛡️ 9. Compliance & Approval

Generated campaign content passes through a compliance layer before delivery.

The compliance workflow can check for:

* Prohibited guarantees
* Potentially inappropriate financial claims
* Required campaign conditions
* Customer opt-in / consent
* Campaign approval status

```text
AI Campaign
     ↓
Compliance Validation
     ↓
 ┌───────────────┐
 │               │
 ▼               ▼
PASS           REVIEW
 │               │
 └───────┬───────┘
         ▼
 Human Approval
```

This creates a **human-in-the-loop** checkpoint before campaign delivery.

---

# 📧 10. Campaign Delivery

Approved campaigns can move into the delivery workflow.

Supported functionality includes:

### Email

* SMTP-based email delivery
* Campaign content
* Approved creative embedding

### SMS

* Simulated SMS dispatch for demonstration purposes

```text
Approved Campaign
       ↓
Delivery Preparation
       ↓
Email / SMS
       ↓
Delivery Record
       ↓
Analytics
```

---

# 🧪 11. A/B Testing

Campaign Studio supports generation of multiple campaign variants.

Example:

```text
Campaign
   │
   ├── Variant A
   │
   └── Variant B
```

Campaign performance can then be analyzed using recorded campaign metrics.

The project includes functionality for:

* Variant generation
* Variant tracking
* Campaign-level analytics
* A/B summary data

---

# 📈 12. Analytics & Performance

The Analytics module provides visibility into campaign activity.

Examples include:

* Campaign delivery
* Engagement
* Conversion funnel
* Campaign performance
* A/B testing results
* Audit records

The system uses SQLite for local campaign and audit persistence.

---

# 🔐 13. Governance & Auditing

The Governance layer maintains traceability across campaign activities.

Records can include:

* Campaign creation
* Compliance checks
* Approval actions
* Delivery activity
* Audit events

This supports a more controlled workflow where AI-generated content is not treated as an uncontrolled final output.

---

# 🖥️ Application Pages

The React application contains the following primary pages:

| Route              | Module                  |
| ------------------ | ----------------------- |
| `/`                | Dashboard               |
| `/customers`       | Customer 360°           |
| `/segments`        | Segments & Insights     |
| `/recommendations` | Product Recommendations |
| `/campaign-studio` | AI Campaign Studio      |
| `/creative-studio` | Creative Studio         |
| `/compliance`      | Compliance & Approval   |
| `/delivery`        | Campaign Delivery       |
| `/analytics`       | Analytics & Performance |
| `/governance`      | Governance & Audits     |

---

# 🛠️ Technology Stack

## Frontend

* **React**
* **TypeScript**
* **Vite**
* **Tailwind CSS**
* **Lucide Icons**
* **Recharts**
* **Axios**

## Backend

* **Python 3.10+**
* **FastAPI**
* **Uvicorn**
* **SQLite**

## Data & Machine Learning

* **Pandas**
* **NumPy**
* **Scikit-learn**
* Feature engineering
* K-Means clustering
* PCA
* Silhouette-based cluster evaluation
* Recommendation scoring

## Generative AI

* **Google Gemini**
* Personalized campaign generation
* Multilingual content generation
* A/B content variants

## Creative Generation

* **Pillow (PIL)**
* Local banner generation

---

# 📂 Project Structure

```text
BankWise_AI_Project/
│
├── backend/
│   ├── main.py
│   ├── routers/
│   │   ├── ab_testing.py
│   │   ├── analytics.py
│   │   ├── approval.py
│   │   ├── campaigns.py
│   │   ├── compliance.py
│   │   ├── creative.py
│   │   ├── customers.py
│   │   ├── delivery.py
│   │   ├── recommendations.py
│   │   └── segments.py
│   │
│   └── services/
│       ├── campaign_service.py
│       └── creative_service.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
│
├── src/
│   ├── campaign/
│   ├── compliance/
│   ├── data/
│   ├── features/
│   ├── genai/
│   ├── privacy/
│   ├── recommendation/
│   └── segmentation/
│
├── ui/
│   ├── analytics.py
│   ├── campaign_delivery.py
│   ├── campaign_studio.py
│   ├── compliance_approval.py
│   ├── creative_studio.py
│   ├── customer_360.py
│   ├── dashboard.py
│   ├── recommendations.py
│   └── segmentation.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── app.py
├── build_features.py
├── finora_db.py
├── inspect_dataset.py
├── requirements.txt
├── .env
└── README.md
```

---

# ⚙️ Installation & Setup

## Prerequisites

Make sure you have:

* Python **3.10, 3.11, or 3.12**
* Node.js **18+**
* npm
* Git

---

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/BankWise-AI.git
cd BankWise-AI
```

---

## 2. Backend Setup

Create a Python virtual environment.

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Create or update `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=your_gemini_model_here

GMAIL_ADDRESS=your_email@example.com
GMAIL_APP_PASSWORD=your_gmail_app_password_here
```

Replace the placeholder values with your own credentials when running the application locally.

> **Security:** Never publish real API keys, passwords, or other secrets to a public repository.

---

## 4. Start FastAPI Backend

From the project root:

```bash
uvicorn backend.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

---

## 5. Start React Frontend

Open a second terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open:

```text
http://localhost:5173
```

---

# 🔎 API Architecture

The backend exposes REST endpoints for major application capabilities.

```text
Frontend
   │
   ▼
FastAPI REST API
   │
   ├── Customers
   ├── Segments
   ├── Recommendations
   ├── Campaigns
   ├── Creative
   ├── Compliance
   ├── Approval
   ├── Delivery
   ├── Analytics
   └── A/B Testing
```

FastAPI's interactive API documentation is available at:

```text
http://localhost:8000/docs
```

when the backend is running.

---

# 🧪 Validation

The project can be validated using the following checks.

### Python compilation

```powershell
python -m compileall backend src ui app.py build_features.py finora_db.py inspect_dataset.py
```

### Frontend production build

```powershell
cd frontend
npm run build
```

The current project has been validated with both Python compilation and the React/Vite production build.

---

# 📊 Data Flow

The analytical data pipeline follows:

```text
Raw Customer Data
        ↓
Data Validation
        ↓
Feature Engineering
        ↓
Customer Features
        ↓
Segmentation
        ↓
Cluster Evaluation
        ↓
Customer Personas
        ↓
Product Eligibility
        ↓
Product Scoring
        ↓
Recommendation Selection
        ↓
Recommendation Validation
        ↓
Campaign Targeting
```

---

# 🧠 AI Architecture

BankWise AI uses separate layers for **predictive/analytical intelligence** and **Generative AI**.

### Machine Learning Layer

Responsible for:

* Feature engineering
* Customer segmentation
* Cluster profiling
* Product eligibility
* Product scoring
* Recommendation selection

### Generative AI Layer

Responsible for:

* Campaign copy
* Personalized messaging
* Multilingual generation
* A/B campaign variants

This separation makes it possible to use structured ML outputs as controlled context for Generative AI.

---

# 🔒 Security & Privacy

This repository is intended as a **demonstration/prototype project**.

For a production banking deployment, additional controls would be required, including:

* Authentication and authorization
* Secure secret management
* Encryption
* API security
* Database security
* PII protection
* Data retention policies
* Regulatory compliance
* Monitoring and incident management

Use **synthetic or anonymized data** when sharing the project publicly.

---

# ⚠️ Disclaimer

BankWise AI is a technology demonstration and is **not a production banking system or financial-advisory service**.

Recommendations, campaigns, scores, and generated content are intended for demonstration purposes. Production deployment would require appropriate validation, security controls, regulatory review, compliance processes, and human oversight.

---

# 🚀 Future Enhancements

Potential future improvements include:

* Real-time customer event processing
* Advanced recommendation models
* Model monitoring and drift detection
* Automated model retraining
* Role-based access control
* Cloud deployment
* Containerization with Docker
* Production-grade database infrastructure
* Advanced campaign attribution
* Real-time A/B testing
* Additional communication channels
* Enhanced compliance rule engines
* Model explainability dashboards

---

# 👨‍💻 Project Highlights

BankWise AI demonstrates an end-to-end application of:

**Machine Learning + Generative AI + Full-Stack Development + Marketing Automation**

The project connects customer intelligence with campaign execution through a controlled workflow:

```text
Understand Customer
        ↓
Segment Customer
        ↓
Recommend Product
        ↓
Explain Recommendation
        ↓
Generate Campaign
        ↓
Generate Creative
        ↓
Validate Compliance
        ↓
Human Approval
        ↓
Deliver Campaign
        ↓
Measure Performance
```

---

## ⭐ Project

**BankWise AI — AI-Powered Banking Marketing Intelligence Platform**

Built as an end-to-end demonstration of AI-assisted personalized marketing for banking and financial services.