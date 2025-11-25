# AdaptEd - Adaptive Assessment Platform

AdaptEd is a web-based platform that enables teachers to upload assessments and automatically generate multiple adapted versions tailored to students with specific learning needs. The platform uses AI to transform content while preserving educational integrity, with mandatory teacher review before student access.

## Core Features

- **Assessment Upload**: Upload PDF, Word, or image-based assessments
- **AI-Powered Adaptation**: Automatically adapt content for various learning needs
- **Student Profiles**: Create detailed profiles with conditions and adaptation settings
- **Multiple Conditions Support**: Dyslexia, Autism, ADHD, Dyscalculia, Anxiety, EAL, and more
- **Teacher Review Workflow**: All adaptations require teacher approval
- **PDF/Word Export**: Generate accessible output documents

## Supported Conditions

- Dyslexia
- Autism Spectrum Condition (ASC)
- ADHD
- Dyscalculia
- Visual Processing Difficulties
- Auditory Processing Difficulties
- Working Memory Difficulties
- Slow Processing Speed
- Test/Performance Anxiety
- English as Additional Language (EAL)

## Tech Stack

- **Backend**: Django 5.x + Django REST Framework
- **Database**: PostgreSQL (SQLite for development)
- **AI**: OpenAI GPT-4o / Azure OpenAI
- **Task Queue**: Celery + Redis
- **Document Processing**: PyPDF2, python-docx, WeasyPrint
- **Frontend**: React + Tailwind CSS (coming soon)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Redis (for Celery)
- PostgreSQL (optional, SQLite works for development)

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your settings (especially OPENAI_API_KEY)

# Run migrations
python manage.py migrate

# Seed initial data
python manage.py seed_data

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Environment Variables

Key environment variables (see `.env.example` for all):

```
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
OPENAI_API_KEY=your-openai-key

# For PostgreSQL:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=adapted_platform
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/user/` - Current user

### Students
- `GET /api/students/` - List students
- `POST /api/students/` - Create student profile
- `GET /api/students/{id}/` - Get student details
- `GET /api/students/{id}/settings/` - Get adaptation settings
- `PUT /api/students/{id}/settings/` - Update adaptation settings

### Assessments
- `GET /api/assessments/` - List assessments
- `POST /api/assessments/` - Upload assessment
- `POST /api/assessments/{id}/generate/` - Generate adaptations
- `GET /api/assessments/{id}/adapted-versions/` - Get adapted versions

### Adapted Assessments
- `GET /api/adapted/` - List adapted assessments
- `POST /api/adapted/{id}/approve/` - Approve adaptation
- `POST /api/adapted/{id}/reject/` - Reject adaptation
- `PUT /api/adapted/{id}/edit/` - Edit adaptation

### Templates
- `GET /api/templates/` - List adaptation templates
- `GET /api/templates/global/` - Get global templates

## Project Structure

```
adapted_platform/
├── accounts/          # User authentication & audit
├── schools/           # School management
├── students/          # Student profiles & settings
├── assessments/       # Assessment upload & management
├── adaptations/       # AI engine & prompt templates
├── api/               # REST API endpoints
└── frontend/          # React frontend (coming soon)
```

## Condition-Specific Adaptations

Each condition has specific adaptations:

### Dyslexia
- Dyslexia-friendly fonts (OpenDyslexic)
- Increased line/letter spacing
- Syllable breaking
- Text-to-speech support
- Cream/coloured backgrounds

### Autism
- Literal language (no idioms/metaphors)
- Explicit instructions
- Consistent terminology
- Clear structure and progress indicators
- No ambiguous language

### ADHD
- Content chunking
- Progress indicators
- Key word highlighting
- Reference panels
- Visual organization

### Anxiety
- Encouraging language
- Hidden timers
- Partial credit visibility
- Calming formatting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For questions or issues, please open a GitHub issue.
