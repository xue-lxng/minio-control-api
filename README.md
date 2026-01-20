# MinIO Control API

A high-performance REST API for managing MinIO object storage buckets and files with Redis caching support.

## Overview

MinIO Control API is a FastAPI-based service that provides a simple and efficient interface for:
- Creating and managing MinIO storage buckets
- Generating secure download links for files
- Caching file links using Redis for improved performance
- Handling image file operations with placeholder support

## Features

✨ **Core Features:**
- 🪣 **Bucket Management** - Create and manage MinIO buckets
- 🔗 **File Link Generation** - Generate secure, time-limited download links
- ⚡ **Redis Caching** - Cache file links for improved performance
- 🖼️ **Image Support** - Specialized handling for image files with placeholder fallback
- 🔐 **CORS Support** - Cross-Origin Resource Sharing enabled for web applications
- 📚 **Interactive API Docs** - Built-in Swagger UI documentation

## Tech Stack

- **Framework:** FastAPI 0.121.1
- **Server:** Uvicorn 0.38.0
- **Storage:** MinIO (via aiobotocore)
- **Caching:** Redis 7.0.1
- **Python:** 3.13+
- **Async:** Full async/await support

## Project Structure

```
mini-control-api/
├── api/
│   └── v1/
│       ├── models/
│       │   ├── request_models/     # Request DTOs
│       │   └── response_models/    # Response DTOs
│       ├── routers/                # API endpoints
│       │   ├── buckets.py          # Bucket management endpoints
│       │   └── files.py            # File operations endpoints
│       └── services/               # Business logic
│           ├── buckets.py
│           └── files.py
├── core/
│   ├── caching/                    # Caching implementations
│   │   └── in_redis.py
│   └── files/                      # File utilities
├── main.py                         # Application entry point
├── settings.py                     # Configuration settings
├── deps.py                         # Dependency injection markers
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
└── .env.example                    # Environment variables template
```

## Installation

### Prerequisites

- Python 3.13+
- MinIO instance
- Redis instance
- pip or poetry

### Local Setup

1. **Clone the repository:**
```bash
git clone https://github.com/GRPUI/mini-control-api.git
cd mini-control-api
```

2. **Create a virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
ENDPOINT_URL=https://your-minio-endpoint.com
ACCESS_KEY=your_access_key
SECRET_KEY=your_secret_key
REDIS_URL=redis://localhost:6379/0
REGION=us-east-1
SECURE=true
```

5. **Run the application:**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Docker Setup

### Build and Run with Docker

```bash
# Build the image
docker build -t mini-control-api .

# Run the container
docker run -p 8000:8000 \
  -e ENDPOINT_URL=https://your-minio-endpoint.com \
  -e ACCESS_KEY=your_access_key \
  -e SECRET_KEY=your_secret_key \
  -e REDIS_URL=redis://redis:6379/0 \
  mini-control-api
```

### Docker Compose

Create a `docker-compose.yml`:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      ENDPOINT_URL: https://your-minio-endpoint.com
      ACCESS_KEY: your_access_key
      SECRET_KEY: your_secret_key
      REDIS_URL: redis://redis:6379/0
      REGION: us-east-1
      SECURE: "true"
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

Run with:
```bash
docker-compose up
```

## API Endpoints

### Buckets

#### Create Bucket
```http
POST /api/v1/buckets/create
Content-Type: application/json

{
  "bucket_name": "my-bucket"
}
```

**Response:**
```json
{
  "bucket_name": "my-bucket",
  "error": null
}
```

### Files

#### Get File Download Link
```http
POST /api/v1/files/image/link
Content-Type: application/json

{
  "project_id": "my-bucket",
  "file_path": "path/to/image.jpg",
  "placeholder_if_not_found": false
}
```

**Response:**
```json
{
  "link": "https://your-minio-endpoint.com/my-bucket/path/to/image.jpg?...",
  "error": null
}
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENDPOINT_URL` | MinIO endpoint URL | - | ✅ |
| `ACCESS_KEY` | MinIO access key | - | ✅ |
| `SECRET_KEY` | MinIO secret key | - | ✅ |
| `REDIS_URL` | Redis connection URL | - | ✅ |
| `REGION` | AWS region | `us-east-1` | ❌ |
| `SECURE` | Use HTTPS for MinIO | `true` | ❌ |

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI:** http://localhost:8000/api/docs
- **OpenAPI Schema:** http://localhost:8000/api/openapi.json

## Development

### Project Dependencies

Key dependencies:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `aiobotocore` - Async AWS SDK for MinIO
- `redis` - Redis client
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

### Code Style

The project follows Python best practices:
- Type hints throughout
- Async/await patterns
- Dependency injection
- Separation of concerns (routers, services, models)

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

## Performance

- **Async Operations:** All I/O operations are non-blocking
- **Redis Caching:** File links are cached to reduce MinIO requests
- **Connection Pooling:** Efficient resource management with aiobotocore
- **Multi-worker Support:** Docker runs with 4 Uvicorn workers

## Security

- ✅ CORS enabled for web applications
- ✅ Environment-based configuration (no hardcoded secrets)
- ✅ Secure credential handling via MinIO SDK
- ✅ Time-limited download links

## Troubleshooting

### Connection Issues

**MinIO Connection Failed:**
- Verify `ENDPOINT_URL` is correct and accessible
- Check `ACCESS_KEY` and `SECRET_KEY` are valid
- Ensure `SECURE` setting matches your MinIO setup

**Redis Connection Failed:**
- Verify Redis is running and accessible
- Check `REDIS_URL` format: `redis://host:port/db`
- Ensure Redis port is not blocked by firewall

### Common Errors

**"Bucket already exists"**
- The bucket creation endpoint returns success if bucket exists
- This is expected behavior

**"File not found"**
- Verify the file path is correct
- Check the file exists in the specified bucket
- Use `placeholder_if_not_found: true` to get a placeholder link

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/api/docs`

## Roadmap

- [ ] File upload endpoints
- [ ] Batch operations
- [ ] Advanced caching strategies
- [ ] Metrics and monitoring
- [ ] Rate limiting
- [ ] Authentication/Authorization

---

**Version:** 0.1.0  
**Last Updated:** 21.01.2026
