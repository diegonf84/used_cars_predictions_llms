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

### Testing
- Feature extraction test suite (`tests/test_llm_extraction.py`)
- 15 test examples covering various scenarios
- Results saved to timestamped files

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Set up environment variables (`.env`):
```bash
GEMINI_API_KEY=your_api_key_here
```

3. Run tests:
```bash
python tests/test_llm_extraction.py
```

## How It Works

1. User provides natural language car description
2. LLM extracts structured features (manufacturer, year, mileage, etc.)
3. Missing features filled with defaults
4. Features validated with Pydantic
5. Model pipeline predicts price with confidence interval

## TODO

- [ ] FastAPI backend with REST endpoints
- [ ] Gradio frontend interface
- [ ] Docker deployment setup
