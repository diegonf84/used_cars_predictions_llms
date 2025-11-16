# Design Decisions & Technical Notes

## Feature Strategy for Seller-Related Variables

### The Problem

The trained XGBoost model expects **14 features**, including:

**Car-related features** (user CAN provide):
- `manufacturer`, `year`, `mileage`, `transmission`, `drivetrain`
- `fuel_type`, `interior_color`, `mpg`
- `accidents_or_damage`, `one_owner`, `personal_use_only`

**Seller-related features** (user CANNOT provide):
- `driver_reviews_num` - Number of reviews for the seller
- `seller_rating` - Rating of the seller/dealer
- `driver_rating` - Driver satisfaction rating

### Why This is a Problem

The model was trained on marketplace data where cars were listed by sellers/dealers. These three features describe the **seller's reputation**, not the car itself.

When a user wants to predict **their own car's price**, they:
1. Are not yet listed on any platform
2. Don't have seller ratings or reviews
3. Only have information about the car itself

### Current Solution (Phase 1)

**Use median values as defaults:**
- `driver_reviews_num` = 64 (median from training data)
- `seller_rating` = 4.5 (median from training data)
- `driver_rating` = 4.7 (median from training data)

**Rationale:**
- Simple and works immediately
- Represents "average" seller quality
- Allows us to make predictions without retraining

**Implemented in:** `backend/app/constants.py`

### Limitations

1. **Accuracy**: Using fixed defaults means we're assuming all cars are sold by "average" sellers
2. **Bias**: Predictions may be slightly biased toward median seller quality
3. **Missing signal**: We lose potentially valuable information about seller quality

### Future Improvements (Potential)

#### Option 1: Retrain Model Without Seller Features
**Pros:**
- More honest representation of car value
- No arbitrary defaults needed
- Cleaner feature set

**Cons:**
- Requires retraining (time/compute)
- May slightly reduce accuracy
- Need to retrain whenever we want to update

#### Option 2: Two Separate Models
**Pros:**
- Model A: For buyers evaluating listings (includes seller features)
- Model B: For sellers pricing their car (excludes seller features)
- Most accurate approach

**Cons:**
- Maintenance overhead (two models)
- More complex architecture
- Doubles model size

#### Option 3: User-Specified Seller Quality
**Pros:**
- Let users specify "dealer" vs "private seller"
- Map to different default values
- More flexibility

**Cons:**
- Requires user to understand seller types
- Still using defaults, just smarter ones

### Recommendation

For **portfolio/demo purposes**: Current solution is fine and demonstrates:
- Understanding of the problem
- Practical engineering decision
- Clear documentation

For **production**: Consider Option 1 (retrain without seller features) for cleaner, more honest predictions.

---

## MPG Estimation Strategy

### The Problem

Users may not know their car's exact MPG.

### Solution

Estimate based on:
1. **Fuel type**: Different base MPG for Gas, Hybrid, Electric, etc.
2. **Year**: Newer cars tend to be more efficient

**Implemented in:** `backend/app/constants.py::estimate_mpg()`

### Estimates

| Fuel Type | Base MPG |
|-----------|----------|
| Gasoline | 25.0 |
| Hybrid | 45.0 |
| Electric | 100.0 (MPGe) |
| Diesel | 30.0 |
| Plug-In Hybrid | 50.0 |

**Adjustments:**
- Cars ≥ 2020: +10%
- Cars ≤ 2015: -10%

---

## LLM Integration Strategy

### Provider Choice

**Primary:** Anthropic Claude Haiku
- Fast response times (~1-2s)
- Excellent structured output
- Cost-effective (~$0.25/MTok)
- Good at following instructions

**Alternative:** OpenAI GPT-4o-mini
- Also fast and cheap
- JSON mode support
- Widely adopted

### Prompt Strategy

Use structured prompts with:
1. Clear field definitions
2. Valid value lists
3. Mapping rules (e.g., "FWD" → "front_wheel_drive")
4. JSON-only output

**Trade-offs:**
- **Accuracy vs Speed**: Haiku is fast but may need careful prompting
- **Cost vs Quality**: Using mini models keeps costs low for portfolio project

---

## Architecture Decisions

### Why FastAPI?

- Modern, fast, async support
- Automatic API documentation (Swagger/ReDoc)
- Pydantic integration for validation
- Type hints throughout

### Why Gradio over Streamlit (initially)?

- Faster to build simple interfaces
- Built-in examples support
- Good for demos
- Can migrate to Streamlit later for more customization

### Why Docker?

- Reproducible deployments
- Easy to share and run
- Production-ready
- Demonstrates DevOps skills for portfolio

---

## Testing Strategy

Focus on:
1. **Unit tests**: Each service independently
2. **Integration tests**: Full prediction pipeline
3. **Edge cases**: Invalid inputs, missing data, LLM failures

**Coverage goal**: >80% for portfolio quality

---

## Future Enhancements (Not in MVP)

1. **Model improvements**: Retrain without seller features
2. **Caching**: Cache LLM responses for similar inputs
3. **Monitoring**: Track prediction accuracy over time
4. **Batch predictions**: Process multiple cars at once
5. **Image support**: Extract features from car photos
6. **Explanations**: SHAP values for prediction interpretability

---

_Last updated: Phase 1 - Project Setup_
