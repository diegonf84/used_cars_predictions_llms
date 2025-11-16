# Used Cars Price Prediction with LLM - Project Plan

## Project Overview

**Goal:** ML application that predicts used car prices from natural language using LLM + XGBoost

**Core Flow:**
1. User describes car in plain English
2. LLM extracts structured features (manufacturer, year, mileage, etc.)
3. XGBoost model predicts price
4. Return price range with confidence

**Portfolio Value:** Demonstrates full-stack ML engineering (LLM integration, model deployment, API, frontend, Docker)

---

## Architecture

```
User Input (text)
    ↓
Frontend (Gradio/Streamlit)
    ↓
FastAPI Backend
    ├── LLM Service → Extract features from text
    └── Model Service → Predict price from features
    ↓
Response (price + range + confidence)
```

---

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **LLM** | Anthropic Claude Haiku | Fast, cheap (~$0.25/MTok), good at structured extraction |
| **Alternative** | OpenAI GPT-4o-mini | Also fast/cheap, JSON mode |
| **Backend** | FastAPI | Modern, async, auto-docs, type hints |
| **Frontend** | Gradio → Streamlit | Gradio for quick MVP, Streamlit for polish |
| **Model** | XGBoost (existing) | Already trained |
| **Validation** | Pydantic v2 | Type safety, FastAPI integration |
| **Containers** | Docker Compose | Easy deployment |
| **Testing** | pytest | Standard Python testing |
| **Env Management** | python-dotenv | Secure config |

---

## Phase-by-Phase Plan

### Phase 1: Project Setup ✅ COMPLETED

**Duration:** 1-2 hours

**Deliverables:**
- ✅ Directory structure (`backend/`, `frontend/`, `tests/`)
- ✅ `constants.py` with feature metadata and valid values
- ✅ `.env.example` for configuration
- ✅ Updated `.gitignore`
- ✅ `DESIGN_DECISIONS.md` documenting feature strategy

**Key Decision:** Use median values for seller features (seller_rating, driver_rating, driver_reviews_num)

---

### Phase 2: LLM Integration Service

**Duration:** 3-4 hours

**Goal:** Extract structured car features from natural language

**Files to Create:**
- `backend/app/services/llm_service.py`

**Key Components:**

1. **LLMService Class**
   - `extract_car_features(user_input: str) → dict`
   - Choose provider (Anthropic/OpenAI)
   - Build structured prompt
   - Parse JSON response
   - Handle errors/retries

2. **Prompt Engineering**
   - Define all 14 features with descriptions
   - List valid values (from `constants.py`)
   - Provide mapping rules (e.g., "FWD" → "front_wheel_drive")
   - Request JSON-only output
   - Add 2-3 examples for few-shot learning

3. **Feature Extraction Strategy**
   - **User CAN provide:** manufacturer, year, mileage, transmission, drivetrain, fuel_type, interior_color, accidents, ownership
   - **Auto-fill defaults:** seller_rating, driver_rating, driver_reviews_num (from constants.py)
   - **Estimate if missing:** mpg (using `estimate_mpg()` from constants.py)

4. **Error Handling**
   - LLM API failures (retry 3x with backoff)
   - Invalid JSON responses (fallback parsing)
   - Missing required fields (use defaults)
   - Unknown categorical values (map to "others")

**Testing:**
- Mock LLM responses for unit tests
- Test with various input formats
- Test missing information handling
- Test edge cases (gibberish input, empty string)

---

### Phase 3: Model Service & Validation

**Duration:** 2-3 hours

**Goal:** Load XGBoost model and make predictions with validation

**Files to Create:**
- `backend/app/services/model_service.py`
- `backend/app/services/validation.py`

**Key Components:**

1. **ModelService Class**
   - Load pickled model on init
   - `predict(features: dict) → dict` with price + range
   - Preprocess features to DataFrame (correct column order!)
   - Calculate confidence interval (simple: ±10% of prediction)
   - Handle prediction errors

2. **Validation Service**
   - Create Pydantic model for CarFeatures
   - Validate numeric ranges (year: 2010-2024, mileage: 0-300k)
   - Validate categorical values (check against constants.py)
   - Auto-map invalid values to "others"
   - Return list of warnings (e.g., "Used default MPG")

3. **Feature Preprocessing**
   - Ensure correct column order (from `MODEL_FEATURES` in constants.py)
   - Convert to pandas DataFrame
   - Handle data types (int, float, str)

4. **MPG Estimation Integration**
   - Use `estimate_mpg()` from constants.py if MPG not provided
   - Base on fuel_type + year

**Testing:**
- Test model loads correctly
- Test predictions with known inputs
- Test validation catches invalid values
- Test edge cases (extreme values, missing features)

---

### Phase 4: FastAPI Backend

**Duration:** 3-4 hours

**Goal:** REST API connecting LLM service + Model service

**Files to Create:**
- `backend/app/main.py` - FastAPI app
- `backend/app/config.py` - Settings management
- `backend/app/schemas/schemas.py` - Request/response models
- `backend/app/routers/predictions.py` - Endpoints
- `backend/requirements.txt` - Dependencies

**Key Endpoints:**

1. **POST /api/v1/predict**
   - Input: `{"user_input": "text description"}`
   - Process: LLM extract → validate → model predict
   - Output: price, range, confidence, extracted features, warnings

2. **GET /health**
   - Check model loaded, LLM configured
   - Return status

3. **GET /api/v1/feature-options**
   - Return valid values for categorical features
   - Useful for frontend dropdowns

**Configuration:**
- Load from `.env` using pydantic-settings
- API keys, model path, ports, environment

**Error Handling:**
- LLM failures → retry then graceful error
- Validation errors → 400 with details
- Model errors → 500 with message
- Add request logging

**CORS:**
- Enable for frontend (localhost during dev)

**Dependencies:**
```
fastapi
uvicorn[standard]
pydantic
pydantic-settings
anthropic (or openai)
pandas
numpy
scikit-learn
xgboost
python-dotenv
httpx
```

**Testing:**
- Use FastAPI TestClient
- Test successful prediction flow
- Test error cases (empty input, LLM failure)
- Test validation errors

---

### Phase 5: Frontend Application

**Duration:** 2-3 hours

**Goal:** User-friendly UI for predictions

**Files to Create:**
- `frontend/app.py` - Gradio or Streamlit app
- `frontend/requirements.txt`

**Choice: Gradio (Recommended for MVP)**
- Faster to build
- Built-in examples support
- Clean default styling
- Easy deployment

**UI Components:**

1. **Input Section**
   - Large text area for car description
   - Placeholder with example
   - Example descriptions (pre-filled buttons)
   - "Predict Price" button

2. **Output Section**
   - Large prominent price display
   - Price range (low - high)
   - Confidence percentage/bar
   - Extracted features in table/list format
   - Warnings (if any)

3. **Polish**
   - Welcome message with instructions
   - Loading indicator during prediction
   - Error messages (backend unavailable, etc.)
   - Clear/reset button

**Backend Connection:**
- Use `requests` library to call FastAPI
- Handle timeout (30s)
- Handle connection errors gracefully
- Set BACKEND_URL from environment

**Examples to Include:**
```
"2020 Toyota Camry, 45k miles, automatic, one owner, no accidents"
"2018 Honda Civic, 60k miles, manual, black interior, clean title"
"Ford F-150 2021, 4x4, automatic, 30k miles, silver"
"BMW 3 Series 2019, AWD, 52k miles, leather interior, personal use"
```

**Testing:**
- Test UI locally
- Test API connection
- Test error display
- Test with various inputs

---

### Phase 6: Testing

**Duration:** 2-3 hours

**Goal:** Comprehensive test coverage

**Files to Create:**
- `tests/conftest.py` - Fixtures
- `tests/test_llm_service.py`
- `tests/test_model_service.py`
- `tests/test_validation.py`
- `tests/test_api.py`

**Test Strategy:**

1. **Unit Tests**
   - LLM service with mocked API calls
   - Model service with sample features
   - Validation logic
   - Each service independently

2. **Integration Tests**
   - Full prediction flow (API endpoint)
   - Error propagation
   - End-to-end with mocked LLM

3. **Test Cases to Cover**
   - Valid complete input
   - Partial input (missing features)
   - Invalid input (garbage text)
   - Edge cases (very old car, high mileage)
   - LLM API failures
   - Model prediction errors

4. **Coverage Goal**
   - Aim for >80% for portfolio quality
   - Focus on critical paths (prediction flow)

**Tools:**
- pytest
- pytest-cov (coverage reporting)
- pytest-mock (mocking)

---

### Phase 7: Docker Containerization

**Duration:** 2-3 hours

**Goal:** Reproducible deployment with Docker

**Files to Create:**
- `backend/Dockerfile`
- `backend/.dockerignore`
- `frontend/Dockerfile`
- `frontend/.dockerignore`
- `docker-compose.yml`

**Docker Strategy:**

1. **Backend Container**
   - Base: python:3.12-slim
   - Install dependencies from requirements.txt
   - Copy app code + models directory
   - Expose port 8000
   - Health check on /health endpoint
   - CMD: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

2. **Frontend Container**
   - Base: python:3.12-slim
   - Install gradio (or streamlit)
   - Copy app.py
   - Expose port 7860 (Gradio) or 8501 (Streamlit)
   - Set BACKEND_URL env var
   - CMD: `python app.py`

3. **Docker Compose**
   - Define both services
   - Backend: expose 8000, mount models volume
   - Frontend: expose 7860, depends_on backend
   - Network: create shared network
   - Environment: load from .env file
   - Health checks + restart policies

**Usage:**
```bash
cp .env.example .env  # Add API key
docker-compose up -d
# Frontend: http://localhost:7860
# Backend: http://localhost:8000/docs
```

**Optimization:**
- Use .dockerignore (exclude .venv, __pycache__, etc.)
- Multi-stage builds (optional, for smaller images)
- Cache pip dependencies

---

### Phase 8: Documentation & Polish

**Duration:** 2-3 hours

**Goal:** Portfolio-ready presentation

**Tasks:**

1. **Update README.md**
   - Project overview with architecture diagram
   - Features list
   - Quick start (Docker)
   - Local development setup
   - API usage examples
   - Technology stack
   - Screenshots/GIFs
   - Environment variables reference

2. **Code Documentation**
   - Docstrings for all public functions
   - Type hints everywhere
   - Comments for complex logic
   - Remove dead code/TODOs

3. **API Documentation**
   - FastAPI auto-generates /docs (Swagger)
   - Add description to endpoints
   - Add request/response examples

4. **Additional Docs** (optional)
   - `docs/DEPLOYMENT.md` - Cloud deployment guide
   - `docs/API.md` - Detailed API reference

5. **Demo Materials**
   - Record GIF of using the app
   - Create example notebook
   - Add to portfolio site

---

### Phase 9: Optional Enhancements

**Future improvements** (not for MVP):

**Features:**
- Multi-turn conversation (LLM asks clarifying questions)
- Image upload (extract features from car photos)
- Compare multiple cars side-by-side
- Show similar cars from dataset
- Price trend over time

**Technical:**
- Retrain model without seller features (cleaner predictions)
- LLM response caching (save costs)
- Model optimization (ONNX, faster inference)
- Add authentication/user accounts
- Rate limiting per user
- Monitoring dashboard (Grafana)

**Deployment:**
- Deploy to cloud (AWS/GCP/Azure)
- CI/CD pipeline (GitHub Actions)
- SSL certificates
- Custom domain

---

## Timeline

| Phase | Duration | Focus |
|-------|----------|-------|
| Phase 1 | 1-2h | Setup ✅ |
| Phase 2 | 3-4h | LLM service |
| Phase 3 | 2-3h | Model service |
| Phase 4 | 3-4h | FastAPI backend |
| Phase 5 | 2-3h | Frontend |
| Phase 6 | 2-3h | Testing |
| Phase 7 | 2-3h | Docker |
| Phase 8 | 2-3h | Documentation |

**Total:** 17-25 hours (3-4 days for production-ready)

**MVP (Phases 1-5):** 11-16 hours (can demo and get feedback)

---

## Success Criteria

**Functional:**
- ✅ User inputs natural language → gets price prediction
- ✅ LLM extraction accuracy >90% on test cases
- ✅ API responds <5 seconds
- ✅ Docker deployment works on any machine
- ✅ Handles errors gracefully

**Quality:**
- ✅ >80% test coverage
- ✅ Clean, documented code
- ✅ Professional UI/UX
- ✅ Complete README with examples
- ✅ No secrets in git

**Portfolio:**
- ✅ Demonstrates LLM integration
- ✅ Shows ML deployment skills
- ✅ Full-stack architecture
- ✅ Production-ready patterns
- ✅ Clear documentation

---

## Key Design Decisions

### 1. Seller Features Problem

**Issue:** Model expects seller_rating, driver_rating, driver_reviews_num which users can't provide

**Solution (Phase 1):** Use median values as defaults
- Documented in `DESIGN_DECISIONS.md`
- Future: Could retrain model without these features

### 2. MPG Estimation

**Issue:** Users may not know exact MPG

**Solution:** Estimate based on fuel_type + year
- Implemented in `constants.py::estimate_mpg()`
- User-provided value takes priority

### 3. LLM Provider

**Choice:** Anthropic Claude Haiku (primary)
- Fast (~1-2s response)
- Cost-effective (~$0.25/MTok)
- Good at structured extraction
- Alternative: OpenAI GPT-4o-mini

### 4. Frontend Framework

**Choice:** Gradio for MVP → Streamlit if needed
- Gradio faster to build
- Good for demos
- Can upgrade later

### 5. Validation Strategy

**Approach:** Pydantic models + constants.py
- Type safety
- Auto-validation
- Map invalid → "others"
- Return warnings to user

---

## Important Notes

**Cost Management:**
- Use cheaper LLM models (Haiku/GPT-4o-mini)
- Consider caching repeated inputs
- Monitor API usage

**Security:**
- Never commit `.env` to git ✅
- Validate all user inputs
- Sanitize LLM outputs
- Use HTTPS in production
- Rate limit API endpoints

**Model Limitations:**
- Predictions based on historical data (2010-2024)
- Assumes "average" seller quality
- May not reflect local markets
- Price ranges are estimates

**Next Steps After MVP:**
1. Get feedback from users
2. Measure prediction accuracy
3. Consider retraining model
4. Add monitoring/analytics
5. Deploy to cloud

---

_Last updated: Phase 1 complete - Ready for Phase 2_
