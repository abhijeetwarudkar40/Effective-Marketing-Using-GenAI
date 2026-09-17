# BankWise AI — AI-Powered Banking Marketing Intelligence Platform

An enterprise-grade marketing intelligence platform designed for banking and financial services, featuring AI campaign generation, explainable ML product recommendations, dynamic banner graphic engine, compliance checks, and multi-channel delivery.

---

## 🏗️ Architecture
- **Frontend**: Modern React + Vite (TypeScript, Tailwind CSS v4, Lucide Icons, Recharts, Axios)
- **Backend API**: FastAPI (Python 3.10+) bridging to ML scoring, local creative PIL engines, SQLite audit database, and Google Gemini GenAI.

---

## 🚀 Quickstart Guide (How to Run the Project)

### Prerequisites
Make sure you have the following installed on your system:
1. **Python** (version 3.10, 3.11, or 3.12)
2. **Node.js** (version 18 or higher) with `npm`

---

### Step 1: Clone or Unzip the Project
Extract the zip file to your preferred folder:
```bash
cd effectivemarket
```

---

### Step 2: Set Up Backend (FastAPI)

1. Open a terminal in the project root folder.
2. (Optional but recommended) Create and activate a Python virtual environment:
   - **Windows:**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI backend server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   > The API will be live at `http://localhost:8000` (API Docs available at `http://localhost:8000/docs`).

---

### Step 3: Set Up Frontend (React + Vite)

1. Open a **second terminal** and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and visit:
   ```
   http://localhost:5173
   ```

---

## 🎯 Key Features & Presentation Walkthrough

1. **Dashboard (`/`)**: Executive overview of customer base, high-value segments, conversion metrics, and model performance.
2. **Customer 360° (`/customers`)**: Deep customer profiles, account balances, digital affinity scores, and retention risks.
3. **Segments & Insights (`/segments`)**: Dynamic persona segmentation distributions and risk categorizations.
4. **Product Recommendations (`/recommendations`)**: ML-driven product recommendations with explainability rationale.
5. **Campaign Studio (`/campaign-studio`)**: Hyper-personalized AI marketing copy generation with multi-product selection and English/Hindi/Marathi language support.
6. **Creative Studio (`/creative-studio`)**: 3 unique local high-resolution marketing banners (1200x675) with one-click regeneration and copyright provenance records.
7. **Compliance & Approval (`/compliance`)**: Automated financial compliance checks detecting prohibited guarantees and verifying opt-in consent.
8. **Campaign Delivery (`/delivery`)**: Gmail SMTP transmission with inline approved banner graphic embedding and simulated SMS dispatch.
9. **Analytics & Performance (`/analytics`)**: Conversion funnels and delivery audit logs from SQLite.
10. **Governance & Audits (`/governance`)**: Human-in-the-loop audit logs and compliance records.
