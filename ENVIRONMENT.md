# ThreatTrace AI — Environment Variables Reference

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `APP_ENV` | `production` | Environment mode (`development`, `staging`, `production`) |
| `DEBUG` | `false` | Enable verbose debugging logs |
| `SECRET_KEY` | `secure-key` | Application cryptographic signing key |
| `DATABASE_URL` | `sqlite+aiosqlite:///./threattrace.db` | SQLAlchemy Async database connection URI |
| `BACKEND_HOST` | `0.0.0.0` | FastAPI server listener host address |
| `BACKEND_PORT` | `8000` | FastAPI listener port |
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:3002` | CORS origin whitelists |
| `MAX_UPLOAD_SIZE_BYTES` | `10485760` | Maximum single raw EML upload payload limit (10MB) |
