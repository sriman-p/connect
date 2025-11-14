# Connect - Enterprise Collaboration Platform

<div align="center">

**A comprehensive enterprise collaboration platform combining the best of Linear, Slack, and Google Workspace**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Django 5.2](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 🚀 Features

### Core Capabilities

- **📁 Project Management** - Linear-style project tracking with issues, labels, and priorities
- **📄 Real-Time Documents** - Google Docs-like collaborative editor with cursor tracking
- **📊 Spreadsheets** - Excel-like sheets with formulas and real-time multi-user editing
- **💬 Messaging** - Slack-style chat with channels and threaded conversations
- **📅 Meetings** - Zoom-style meeting management with participants and recordings
- **📎 File Management** - Google Drive-like file storage with versioning and sharing
- **✅ Approvals** - Multi-step approval workflows (sequential, parallel, any-approver)
- **🔒 Passkey Authentication** - WebAuthn/FIDO2 passwordless authentication

### Technical Features

- **Real-time Collaboration** - WebSocket-based cursor tracking and live editing
- **Operational Transformation** - Conflict-free concurrent editing
- **Bitmap RBAC** - Memory-efficient permission system (64 permissions in 8 bytes)
- **JWT Authentication** - Secure token-based auth with refresh tokens
- **Comprehensive REST API** - 60+ endpoints with OpenAPI documentation
- **Admin Interfaces** - Full Django admin for all models
- **TypeScript** - Fully typed frontend with strict mode
- **Animations** - Smooth Framer Motion animations throughout

---

## 🏗️ Architecture

### Backend Stack

- **Django 5.2.8** - Web framework
- **Django REST Framework 3.16.1** - API framework
- **Django Channels 4.3.1** - WebSocket support
- **PostgreSQL 15** - Primary database
- **Redis 7** - WebSocket channel layer & caching
- **Daphne** - ASGI server

### Frontend Stack

- **Next.js 16** - React framework with App Router
- **TypeScript 5** - Type safety
- **Tailwind CSS v4** - Styling
- **Framer Motion** - Animations
- **TanStack Query 5.90.8** - Data fetching
- **Tiptap** - Rich text editor
- **Y.js** - CRDT for real-time collaboration

---

## 📦 Installation

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/connect.git
   cd connect
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - API Docs: http://localhost:8000/api/docs

### Manual Installation

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure database
createdb connect
# Update .env with your database credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Start development server
python manage.py runserver
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Start development server
npm run dev
```

---

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available configuration options.

#### Required Variables

- `SECRET_KEY` - Django secret key (50+ characters)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `NEXT_PUBLIC_API_URL` - Backend API URL for frontend

#### Optional Variables

- `DEBUG` - Enable debug mode (False in production)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS` - Frontend URLs for CORS
- `AWS_*` - AWS S3 configuration for file uploads
- `EMAIL_*` - SMTP configuration for emails
- `SENTRY_DSN` - Sentry error tracking

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/api/schema

### API Endpoints

#### Authentication (11 endpoints)
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - JWT login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `POST /api/auth/passkey/register/init/` - Start passkey registration
- `POST /api/auth/passkey/register/complete/` - Complete passkey registration
- `POST /api/auth/passkey/authenticate/init/` - Start passkey auth
- `POST /api/auth/passkey/authenticate/complete/` - Complete passkey auth
- `GET /api/auth/passkey/credentials/` - List passkeys
- `DELETE /api/auth/passkey/credentials/{id}/` - Delete passkey

#### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Get project details
- `PATCH /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

#### Issues
- `GET /api/issues/` - List issues
- `POST /api/issues/` - Create issue
- `GET /api/issues/{id}/` - Get issue details
- `PATCH /api/issues/{id}/` - Update issue
- `DELETE /api/issues/{id}/` - Delete issue
- `GET /api/issues/{id}/comments/` - Get issue comments
- `POST /api/issues/{id}/comments/` - Add comment

#### Documents
- `GET /api/documents/` - List documents
- `POST /api/documents/` - Create document
- `GET /api/documents/{id}/` - Get document
- `PATCH /api/documents/{id}/` - Update document
- `DELETE /api/documents/{id}/` - Delete document
- `GET /api/documents/{id}/versions/` - Get versions
- `POST /api/documents/{id}/duplicate/` - Duplicate document

#### Spreadsheets
- `GET /api/spreadsheets/` - List spreadsheets
- `POST /api/spreadsheets/` - Create spreadsheet
- `GET /api/spreadsheets/{id}/` - Get spreadsheet
- `PATCH /api/spreadsheets/{id}/` - Update spreadsheet
- `POST /api/cells/bulk_update/` - Bulk update cells

#### Meetings
- `GET /api/meetings/` - List meetings
- `POST /api/meetings/` - Create meeting
- `GET /api/meetings/{id}/` - Get meeting
- `POST /api/meetings/{id}/start/` - Start meeting
- `POST /api/meetings/{id}/end/` - End meeting
- `POST /api/meetings/{id}/join/` - Join meeting
- `GET /api/meetings/{id}/participants/` - Get participants

#### Approvals
- `GET /api/approvals/requests/` - List approval requests
- `POST /api/approvals/requests/` - Create request
- `POST /api/approvals/requests/{id}/approve/` - Approve
- `POST /api/approvals/requests/{id}/reject/` - Reject
- `GET /api/approvals/workflows/` - List workflows

#### Files
- `GET /api/files/` - List files
- `POST /api/files/` - Upload file
- `GET /api/files/{id}/` - Get file details
- `POST /api/files/{id}/download/` - Track download
- `POST /api/files/{id}/share/` - Share file
- `GET /api/files/{id}/versions/` - Get versions

#### WebSocket Endpoints
- `ws://localhost:8000/ws/chat/{channel_id}/` - Chat messaging
- `ws://localhost:8000/ws/documents/{document_id}/` - Document collaboration
- `ws://localhost:8000/ws/spreadsheets/{spreadsheet_id}/` - Spreadsheet collaboration

---

## 🎨 Frontend Pages

### Public Pages
- `/` - Landing page
- `/login` - Login with JWT or Passkey
- `/register` - User registration

### Authenticated Pages
- `/dashboard` - Main dashboard with widgets
- `/projects` - Projects list
- `/projects/{id}` - Project detail with issues
- `/issues` - Issues table view
- `/issues/{id}` - Issue detail
- `/documents` - Documents grid
- `/documents/{id}` - Collaborative editor
- `/spreadsheets` - Spreadsheets list
- `/spreadsheets/{id}` - Collaborative spreadsheet
- `/meetings` - Meetings calendar
- `/meetings/{id}` - Meeting detail
- `/files` - Files grid view
- `/approvals` - Approval requests
- `/settings` - User settings (profile, security, notifications, passkeys)

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
python manage.py test
```

### Frontend Tests

```bash
cd frontend
npm test
```

### E2E Tests

```bash
cd frontend
npm run test:e2e
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure PostgreSQL with connection pooling
- [ ] Set up Redis persistence
- [ ] Configure HTTPS/SSL certificates
- [ ] Set `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
- [ ] Configure email backend (SMTP)
- [ ] Set up AWS S3 for file storage
- [ ] Enable Sentry for error tracking
- [ ] Configure backup strategy
- [ ] Set up monitoring (Prometheus/Grafana)

### Docker Production Deployment

```bash
# Build images
docker-compose build

# Start with nginx profile
docker-compose --profile production up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale backend=3
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests.

---

## 📊 Database Schema

### Core Models

#### Users & Authentication
- `User` - Extended Django user model
- `PasskeyCredential` - WebAuthn credentials
- `PasskeyAuthenticationAttempt` - Auth attempt logs

#### Workspaces & Projects
- `Workspace` - Tenant isolation
- `WorkspaceMember` - Membership with permissions
- `Project` - Project container
- `ProjectMember` - Project team

#### Issues & Tasks
- `Issue` - Task/bug tracking
- `Label` - Issue categorization
- `IssueComment` - Threaded discussions
- `IssueAttachment` - File attachments

#### Documents
- `Document` - Document storage
- `DocumentVersion` - Version history
- `DocumentSession` - Real-time sessions
- `DocumentOperation` - Operational transform log
- `DocumentComment` - Inline comments

#### Spreadsheets
- `Spreadsheet` - Spreadsheet container
- `Sheet` - Individual sheets
- `Cell` - Cell data with formulas
- `NamedRange` - Named cell ranges
- `Chart` - Data visualizations

#### Meetings
- `Meeting` - Meeting scheduling
- `MeetingParticipant` - Attendees
- `MeetingNote` - Meeting notes
- `MeetingRecording` - Video recordings

#### Approvals
- `ApprovalWorkflow` - Workflow templates
- `ApprovalStep` - Sequential steps
- `ApprovalRequest` - Individual requests
- `ApprovalAction` - Approval actions

#### Files
- `File` - File metadata
- `FileFolder` - Folder hierarchy
- `FileShare` - Sharing permissions
- `FileVersion` - Version control

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint/Prettier for TypeScript
- Write tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Django team for the amazing web framework
- Next.js team for the React framework
- All open-source contributors

---

## 📞 Support

- 📧 Email: support@connect.example.com
- 💬 Discord: https://discord.gg/connect
- 📚 Documentation: https://docs.connect.example.com
- 🐛 Issues: https://github.com/yourusername/connect/issues

---

## 🗺️ Roadmap

### Q1 2025
- [ ] Mobile apps (iOS/Android)
- [ ] Advanced analytics dashboard
- [ ] Integrations (GitHub, Jira, Slack)
- [ ] AI-powered features

### Q2 2025
- [ ] Video conferencing integration
- [ ] Advanced reporting
- [ ] Custom workflows
- [ ] API rate limiting

### Q3 2025
- [ ] Multi-language support
- [ ] Advanced search with Elasticsearch
- [ ] Audit logs
- [ ] SSO/SAML support

---

<div align="center">

**Built with ❤️ by the Connect Team**

[Website](https://connect.example.com) • [Docs](https://docs.connect.example.com) • [Blog](https://blog.connect.example.com)

</div>
