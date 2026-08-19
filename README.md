# Online Coding Judge

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg)](https://vitejs.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Tests-89%20Passed-success.svg)](#running-tests)

A modern, production-grade Online Coding Judge platform engineered with a high-performance **FastAPI** backend, **MSSQL** persistence with repository abstraction, an isolated **code execution engine** with AST-level security analysis, and an interactive **React + Monaco Editor** web interface.

---

## Key Features

- **Problem Catalog & Filtering**: Browse coding challenges with difficulty filters (Easy, Medium, Hard), search by keyword, tag navigation, and pagination.
- **In-Browser IDE**: Monaco Editor integration supporting syntax highlighting, auto-indentation, and configurable templates.
- **Sandboxed Execution Engine**:
  - AST-based static analysis to detect and block malicious standard imports (`os`, `subprocess`, `sys`, dynamic imports).
  - Isolated subprocess execution with strict memory, runtime timeout (default 2.0s), and output size limits.
  - Normalized whitespace and output comparator.
- **Real-Time Verdicts**: Instant evaluation against public and hidden test cases with verdicts:
  - `Accepted (AC)`
  - `Wrong Answer (WA)`
  - `Time Limit Exceeded (TLE)`
  - `Runtime Error (RE)`
  - `Compilation/Syntax Error (CE)`
- **Authentication & Security**:
  - Secure password hashing using `bcrypt`.
  - Stateless JWT authentication (`HS256`) with automatic expiration and frontend interception.
  - Security headers middleware (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`).
  - Strict CORS origin enforcement.
- **Submissions & Analytics**:
  - User submission history with detailed per-test-case diagnostics and execution time metrics.
  - Global user statistics dashboard tracking acceptance rate, solved count, and recent activity.
- **Theme Support**: Built-in Dark / Light mode toggle with CSS custom properties design tokens.

---

## Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Server**: [Uvicorn](https://www.uvicorn.org/)
- **ORM & Database**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) with `pyodbc` for Microsoft SQL Server (MSSQL), plus in-memory fallback repositories
- **Authentication**: `python-jose` (JWT), `passlib` & `bcrypt`
- **Validation & Settings**: `pydantic v2`, `pydantic-settings`
- **Testing**: `pytest`, `httpx`

### Frontend
- **Framework**: [React 18](https://react.dev/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Code Editor**: [@monaco-editor/react](https://github.com/suren-atoyan/monaco-react)
- **Routing**: `react-router-dom v6`
- **Icons**: `lucide-react`
- **Styling**: Vanilla CSS Design System with CSS variables and responsive grid

---

## Project Structure

```text
online-coding-judge/
├── app/                              # Backend Application
│   ├── core/                         # Global configurations, logging, security settings
│   ├── database/                     # DB connection & SQLAlchemy models
│   ├── dependencies/                 # FastAPI dependency injection providers
│   ├── exceptions/                   # Custom application exceptions & handlers
│   ├── execution/                    # Sandboxed runner, AST validator, test case executor
│   ├── models/                       # Domain entities & status enums
│   ├── repositories/                 # Repository layer (MSSQL & In-Memory)
│   ├── routes/                       # REST API endpoint routers
│   ├── schemas/                      # Pydantic request/response schemas
│   ├── security/                     # Password hashing & JWT token services
│   ├── services/                     # Business logic layer
│   └── main.py                       # FastAPI application entrypoint & middleware
│
├── frontend/                         # React Frontend Application
│   ├── index.html                    # HTML entrypoint
│   ├── vite.config.js                # Vite build configuration
│   ├── package.json                  # Frontend dependencies & scripts
│   └── src/
│       ├── components/               # UI components (CodeEditor, Navbar, StatCard, etc.)
│       ├── context/                  # AuthContext and ThemeContext
│       ├── pages/                    # Application views (Dashboard, Problems, Submissions)
│       ├── services/                 # API client & HTTP interceptors
│       ├── App.jsx                   # Route declarations
│       ├── index.css                 # Global design system & theme variables
│       └── main.jsx                  # React DOM mount point
│
├── tests/                            # Comprehensive Test Suite (89 tests)
│   ├── test_execution_engine.py      # Sandboxing, timeouts, AST analysis tests
│   ├── test_security_hardening.py    # Security headers, injection protection tests
│   ├── test_submission_service.py    # Verdict generation & submission tests
│   ├── test_user_service.py          # User management & authentication tests
│   └── ...
│
├── .env.example                      # Root backend environment template
├── requirements.txt                  # Python package requirements
├── .gitignore                        # Git ignore specifications
└── README.md                         # Project documentation
```

---

## Getting Started

### Prerequisites
- **Python**: `3.10` or higher
- **Node.js**: `18.0.0` or higher & `npm`
- **Database** *(Optional)*: Microsoft SQL Server (SQLEXPRESS or LocalDB) with ODBC Driver 18 for SQL Server.

---

### Backend Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Junaid-786-29/online-coding-judge.git
   cd online-coding-judge
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` as needed:
   ```env
   APP_ENV=development
   DATABASE_URL=mssql+pyodbc://@localhost\SQLEXPRESS/OnlineCodingJudge?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes
   JWT_SECRET_KEY=your-secure-jwt-secret-key-here
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   TIME_LIMIT_SECONDS=2.0
   MAX_OUTPUT_SIZE=1000000
   MAX_SOURCE_CODE_SIZE=50000
   MAX_INPUT_SIZE=50000
   MAX_TEST_CASES_PER_SUBMISSION=100
   ```

5. **Start the FastAPI backend server**:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   The backend API will be available at `http://127.0.0.1:8000`.  
   Interactive API documentation (Swagger UI) is accessible at `http://127.0.0.1:8000/docs`.

---

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure frontend environment**:
   ```bash
   cp .env.example .env
   ```
   Ensure `.env` contains:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   ```

4. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   The frontend application will be running at `http://localhost:5173`.

---

## API Endpoints

| Category | Method | Endpoint | Auth Required | Description |
| :--- | :--- | :--- | :---: | :--- |
| **System** | `GET` | `/health` | No | System health check and uptime status |
| **Auth** | `POST` | `/api/v1/auth/register` | No | Register a new user account |
| **Auth** | `POST` | `/api/v1/auth/login` | No | Authenticate user & issue JWT token |
| **Auth** | `GET` | `/api/v1/auth/me` | Yes | Retrieve authenticated user profile |
| **Problems** | `GET` | `/api/v1/problems` | No | List problems with search, difficulty, and pagination |
| **Problems** | `GET` | `/api/v1/problems/{id}` | No | Get problem details and sample test cases |
| **Problems** | `POST` | `/api/v1/problems` | Yes | Create a new problem |
| **Test Cases** | `GET` | `/api/v1/problems/{id}/test-cases` | No | Get visible sample test cases for a problem |
| **Test Cases** | `POST` | `/api/v1/problems/{id}/test-cases` | Yes | Add a new test case to a problem |
| **Submissions** | `POST` | `/api/v1/submissions` | Yes | Submit code for evaluation against all test cases |
| **Submissions** | `GET` | `/api/v1/submissions` | Yes | Get submission history with filters and pagination |
| **Submissions** | `GET` | `/api/v1/submissions/{id}` | Yes | Get detailed execution verdict for a submission |
| **Submissions** | `GET` | `/api/v1/submissions/user/stats` | Yes | Get aggregated user performance metrics |

---

## Running Tests

The test suite contains 89 automated tests covering execution isolation, security analysis, authentication, repository implementations, and business logic.

Run the test suite using `pytest`:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific test module
pytest tests/test_execution_engine.py
pytest tests/test_security_hardening.py
```

---

## Security & Sandboxing Architecture

1. **AST Static Inspection**: Code is parsed into an Abstract Syntax Tree (AST) before execution. Submissions attempting to import restricted modules (`os`, `subprocess`, `sys`, `socket`, `shutil`, etc.) or invoke dynamic imports (`__import__`) are rejected immediately without spawning processes.
2. **Process Isolation & Timeouts**: Subprocesses are executed with strict time limits (`TIME_LIMIT_SECONDS`) to prevent infinite loops and denial-of-service.
3. **Payload Truncation**: Standard output and error streams are capped at `MAX_OUTPUT_SIZE` to prevent memory exhaustion attacks.
4. **Security Headers**: Standard OWASP HTTP response headers are injected into every response.

---

## License

Copyright (c) 2026 Junaid Khan. All Rights Reserved.

This project and its source code are proprietary to Junaid Khan.

No part of this project may be copied, reproduced, modified, distributed, published, sublicensed, or used for commercial purposes without explicit written permission from the copyright holder.

Unauthorized use, reproduction, distribution, or modification of this project is prohibited.
