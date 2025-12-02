# Pokemon GO Tracker

A comprehensive web application for tracking Pokemon GO events and analyzing Pokemon screenshots to calculate IVs (Individual Values).

## Features

### 1. Event Tracking
- **Automatic News Crawling**: Fetches the latest Pokemon GO events, community days, and news
- **Email Notifications**: Sends automatic email alerts when new events are published
- **Event Summaries**: Displays organized event information with images and categories
- **Scheduled Updates**: Runs a cron job to check for new events every 30 minutes (configurable)

### 2. IV Calculator (Poke Genie Alternative)
- **Screenshot Analysis**: Upload Pokemon screenshots to analyze IVs
- **OCR Technology**: Uses OpenCV and Tesseract for image text extraction
- **Detailed Stats**: Shows CP, HP, Level, and individual Attack/Defense/Stamina IVs
- **Battle Ratings**: Provides ratings for PvP battles and Raids
- **Training Recommendations**: Suggests whether to power up and best use cases
- **Move Recommendations**: Pokemon-specific moveset suggestions

### 3. Modern UI
- **Next.js Frontend**: Fast, responsive interface with Tailwind CSS
- **Real-time Updates**: Live event feed and instant analysis results
- **Drag & Drop Upload**: Easy screenshot upload interface
- **Mobile Friendly**: Responsive design for all devices

## Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **PostgreSQL**: Relational database for storing events and analyses
- **SQLAlchemy**: ORM for database operations
- **SendGrid**: Email delivery service
- **OpenCV + Tesseract**: Image processing and OCR
- **APScheduler**: Cron job scheduling
- **Beautiful Soup**: Web scraping

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Dropzone**: File upload interface
- **Axios**: HTTP client

### Infrastructure
- **Docker & Docker Compose**: Containerization
- **Redis**: Caching and task queue
- **Alembic**: Database migrations

## Project Structure

```
pokemon-go-tracker/
├── backend/
│   ├── app/
│   │   ├── api/                    # API route handlers
│   │   │   ├── events.py          # Event endpoints
│   │   │   └── analysis.py        # IV analysis endpoints
│   │   ├── core/                   # Core configuration
│   │   │   ├── config.py          # Settings and environment
│   │   │   └── database.py        # Database connection
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── event.py           # Event model
│   │   │   └── pokemon_analysis.py # Analysis model
│   │   ├── services/               # Business logic
│   │   │   ├── crawler_service.py  # Web scraping
│   │   │   ├── email_service.py    # Email notifications
│   │   │   └── iv_calculator.py    # IV calculation
│   │   ├── main.py                 # FastAPI app
│   │   └── scheduler.py            # Cron job scheduler
│   ├── alembic/                    # Database migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py                      # Application entry point
├── frontend/
│   ├── app/                        # Next.js app directory
│   │   ├── page.tsx               # Events listing page
│   │   ├── analyzer/
│   │   │   └── page.tsx           # IV analyzer page
│   │   ├── layout.tsx             # Root layout
│   │   └── globals.css            # Global styles
│   ├── components/                 # React components
│   │   ├── EventCard.tsx          # Event display card
│   │   └── AnalysisResult.tsx     # IV analysis results
│   ├── lib/
│   │   └── api.ts                 # API client
│   ├── package.json
│   ├── Dockerfile
│   └── next.config.js
├── docker-compose.yml              # Docker orchestration
├── .env.example                    # Environment template
└── README.md
```

## Installation & Setup

### Prerequisites
- Docker and Docker Compose
- SendGrid API key (for email notifications)

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
```bash
cd pokemon-go-tracker
```

2. **Set up environment variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your SendGrid credentials
nano .env
```

3. **Start all services with Docker Compose**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis (port 6379)
- FastAPI backend (port 8000)
- Next.js frontend (port 3000)

4. **Run database migrations**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Tesseract OCR**
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt-get install tesseract-ocr`
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

4. **Set up PostgreSQL**
```bash
# Create database
createdb pokemon_go_db
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

6. **Run migrations**
```bash
alembic upgrade head
```

7. **Start the backend**
```bash
python run.py
```

#### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Start development server**
```bash
npm run dev
```

## Configuration

### Environment Variables

#### Backend (.env or docker-compose.yml)
- `DATABASE_URL`: PostgreSQL connection string
- `SENDGRID_API_KEY`: Your SendGrid API key
- `SENDGRID_FROM_EMAIL`: Sender email address
- `NOTIFICATION_EMAIL`: Email to receive notifications
- `CRAWLER_INTERVAL_MINUTES`: How often to check for new events (default: 30)
- `POKEMONGO_NEWS_URL`: Pokemon GO news source URL

#### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

### Cron Job Configuration

The crawler runs automatically every 30 minutes (configurable in [backend/app/core/config.py](backend/app/core/config.py:28)).

To manually trigger a crawl:
```bash
curl -X POST http://localhost:8000/api/events/crawl
```

## API Documentation

### Events API

#### Get All Events
```
GET /api/events?skip=0&limit=20
```

#### Get Single Event
```
GET /api/events/{event_id}
```

#### Trigger Manual Crawl
```
POST /api/events/crawl
```

### Analysis API

#### Upload Screenshot
```
POST /api/analysis/upload
Content-Type: multipart/form-data
Body: file=<image_file>
```

#### Get Analysis History
```
GET /api/analysis/history?skip=0&limit=20
```

#### Get Single Analysis
```
GET /api/analysis/{analysis_id}
```

## How to Use

### Event Tracking
1. The app automatically crawls Pokemon GO news every 30 minutes
2. New events are displayed on the home page
3. You'll receive email notifications for new events
4. Click on any event card to read the full details

### IV Calculator
1. Open Pokemon GO and navigate to a Pokemon's info screen
2. Take a screenshot showing CP, HP, and Pokemon name
3. Go to the "IV Analyzer" tab
4. Drag & drop or click to upload your screenshot
5. View detailed IV analysis and recommendations

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

### Adding New Pokemon

Edit [backend/app/services/iv_calculator.py](backend/app/services/iv_calculator.py:18) and add base stats to `POKEMON_BASE_STATS` dictionary.

## Troubleshooting

### Crawler Not Finding Events
The crawler uses mock data if it can't parse the Pokemon GO website. Update the selectors in [backend/app/services/crawler_service.py](backend/app/services/crawler_service.py:31) to match the current website structure.

### OCR Not Working
- Ensure Tesseract is installed correctly
- Set `TESSERACT_CMD` in your environment if it's not in PATH
- Try clearer screenshots with better lighting

### Email Not Sending
- Verify your SendGrid API key is correct
- Check that your sender email is verified in SendGrid
- Review SendGrid logs for delivery issues

## Future Improvements

- [ ] Support for more Pokemon (expand base stats database)
- [ ] PvP IV ranking calculator
- [ ] Event calendar view
- [ ] User accounts and personalized notifications
- [ ] Mobile app (React Native)
- [ ] Integration with Pokemon GO Hub API
- [ ] Multi-language support
- [ ] Dark mode

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is for educational purposes only. Pokemon and Pokemon GO are trademarks of Nintendo, Creatures Inc., and GAME FREAK Inc.

## Disclaimer

This is an unofficial fan-made tool and is not affiliated with, endorsed by, or connected to Niantic, Nintendo, The Pokemon Company, or any of their affiliates.

## Support

For issues, questions, or suggestions, please open an issue on the project repository.

---

Built with ❤️ for Pokemon GO Trainers
