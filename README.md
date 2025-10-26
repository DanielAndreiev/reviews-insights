# Reviews Insights API

API for analyzing Apple App Store reviews using LLM. Collects reviews, performs sentiment analysis, extracts keywords, and generates actionable insights.

## Quick Start

```bash
# Clone repository
git clone https://github.com/DanielAndreiev/reviews-insights.git
cd reviews-insights

# Create .env file
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Start services
docker-compose up -d

# Apply migrations
docker exec api python -m alembic upgrade head
```

API available at: `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

For a complete analysis example, see [SAMPLE_REPORT.md](SAMPLE_REPORT.md) showcasing insights for Nebula app.

## API Endpoints

**Collect Reviews**
```bash
POST /api/v1/reviews/apple-store/collect
Content-Type: application/json

{"app_id": "1459969523", "limit": 50}
```

**Run Analysis**
```bash
POST /api/v1/reviews/apple-store/analyze
Content-Type: application/json

{"app_id": "1459969523"}
```

**Get Metrics**
```bash
GET /api/v1/reviews/apple-store/metrics?app_id=1459969523
```

**Export Data**
```bash
GET /api/v1/reviews/apple-store/export?app_id=1459969523
```

## Approach & Design Decisions

**Architecture:** Clean Architecture chosen for clear separation of concerns, making the system maintainable and testable. Each layer has a single responsibility, allowing easy modifications without affecting others.

**Technology Choices:**
- **FastAPI:** Async support for high concurrency, auto-generated API docs, Pydantic validation
- **PostgreSQL:** Reliable ACID compliance for data integrity, complex queries for aggregations
- **SQLAlchemy 2.0:** Native async support, type safety, prevents N+1 queries
- **Redis:** Fast caching layer, ready for future background job queues

**Provider Pattern:** Extensible design for collectors and LLM services - easy to add new data sources (Google Play) or LLM providers (Anthropic, local models) without changing core logic.

**Performance:** Parallel LLM processing. Async throughout the stack for non-blocking I/O.

**Database:** Normalized schema with separate tables for reviews, analysis, and insights.

**LLM Integration:** Prompts and system messages stored in separate files for easy versioning, A/B testing, and non-technical team members to iterate on prompts.

## Tech Stack

- FastAPI, Python 3.12
- PostgreSQL, SQLAlchemy, Alembic
- OpenAI API (GPT-4o-mini)
- Redis
- Docker, Poetry


## Project Structure

```
src/
├── application/       # Business logic
├── domain/           # Domain models
├── infrastructure/   # External services
├── presentation/     # API endpoints
└── config/           # Configuration
```

## Development

```bash
# Linters
docker exec api poetry run black src/
docker exec api poetry run ruff check src/
docker exec api poetry run mypy -p src

# Migrations
docker exec api python -m alembic revision --autogenerate -m "description"

# Logs
docker-compose logs -f api
```

## Example Response

```json
{
  "app_id": "544007664",
  "total_reviews": 70,
  "average_rating": 2.96,
  "ratings_summary": {"1": 29, "5": 26},
  "sentiments_summary": {"negative": 39, "positive": 25},
  "top_keywords": ["excessive ads", "user frustration"],
  "top_insights": ["Reduce ad frequency", "Implement premium version"]
}
```

## License

MIT
