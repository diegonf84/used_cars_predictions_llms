# Used Cars Price Prediction with LLM Integration

ML application that predicts used car prices from natural language descriptions using XGBoost and Google Gemini API.

## What's Built

### Phase 1: Project Structure ✅
- Constants and metadata (`backend/app/constants.py`)
- Feature definitions and default values
- MPG estimation logic

### Phase 2: LLM Integration ✅
- Natural language feature extraction (`backend/app/services/llm_service.py`)
- Google Gemini API integration (`gemini-2.5-flash`)
- Structured prompt engineering with few-shot learning
- Automatic default filling for missing features

### Phase 3: Model Service & Validation ✅
- Model pipeline loading with joblib (`backend/app/services/model_service.py`)
- Price prediction with confidence intervals
- Pydantic validation (`backend/app/services/validation.py`)
- User-friendly warning generation

### Phase 4: FastAPI Backend ✅
- FastAPI application with CORS support (`backend/app/main.py`)
- REST API endpoints (`backend/app/api/endpoints.py`)
  - `POST /api/v1/predict` - Price prediction from natural language
  - `GET /api/v1/health` - Health check endpoint
- Request/response schemas (`backend/app/schemas/api_schemas.py`)
- Service initialization at startup (singleton pattern)
- Error handling and logging

### Testing
- Feature extraction test suite (`tests/test_llm_extraction.py`)
  - 15 test examples covering various scenarios
  - Results saved to timestamped files
- API endpoint tests (`tests/test_api.py`)
  - Health check validation
  - Prediction endpoint testing
  - Error handling verification

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Set up environment variables (`.env`):
```bash
GEMINI_API_KEY=your_api_key_here
```

3. Run the FastAPI server:
```bash
uvicorn backend.app.main:app --reload
```

4. Run tests:
```bash
# Test LLM feature extraction
python tests/test_llm_extraction.py

# Test API endpoints (server must be running)
python tests/test_api.py
```

5. Access the API:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health
- Prediction: POST http://localhost:8000/api/v1/predict

## How It Works

1. User provides natural language car description
2. LLM extracts structured features (manufacturer, year, mileage, etc.)
3. Missing features filled with defaults
4. Features validated with Pydantic
5. Model pipeline predicts price with confidence interval

## Using the API

### Interactive Testing (Browser)
The easiest way to test the API is using the built-in Swagger UI:

1. Start the server: `uvicorn backend.app.main:app --reload`
2. Open http://localhost:8000/docs in your browser
3. Click on `POST /api/v1/predict`
4. Click **"Try it out"**
5. Enter your request and click **"Execute"**

### Request Format
All requests must include the `"description"` key:

```json
{
  "description": "2020 Toyota Camry, 45k miles, automatic, clean title"
}
```

### Response Format
```json
{
  "price": 25000,
  "price_min": 22500,
  "price_max": 27500,
  "confidence": 0.9,
  "warnings": [
    "Using default seller rating (average seller quality)",
    "Using default driver rating (average driver quality)"
  ]
}
```

### Example Descriptions
- `"2020 Toyota Camry, 45k miles, automatic transmission, one owner, no accidents"`
- `"Used Honda Civic 2018"`
- `"Ford F-150 2021, 4x4, automatic, 30k miles, gray interior"`
- `"2020 Toyota Prius hybrid, 40k miles, CVT, 55 mpg, no accidents"`

## TODO

- [x] FastAPI backend with REST endpoints
- [ ] Gradio frontend interface
- [ ] Docker deployment setup
