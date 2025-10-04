# Generic Matching App Skeleton

A Flask-based matching application providing core functionality for user authentication, profiles, matching logic, and chat functionality. This skeleton is designed to be extensible and suitable for building various types of matching applications.

## Features

### Core Functionality
- **Authentication System**: User registration, login, logout with secure password hashing
- **Profile Management**: Editable user profiles with name, age, gender, bio, tags, location  
- **Matching Logic**: Like/dislike system with mutual matching detection
- **Chat System**: Basic messaging between matched users
- **REST API**: RESTful endpoints for all core functionality

### Technical Stack
- **Backend**: Flask + Flask-Login + Flask-SQLAlchemy + Flask-WTF
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **Frontend**: TailwindCSS via CDN, vanilla JavaScript
- **Forms**: WTForms with CSRF protection

## Project Structure

```
/project-root
├── app.py                    # Main Flask application
├── models.py                 # Database models (User, Profile, Like, Match, Message)
├── forms.py                  # WTForms for all user inputs
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── routes/                   # Route blueprints
│   ├── __init__.py
│   ├── auth.py              # Authentication routes
│   ├── profile.py           # Profile management routes
│   ├── match.py             # Matching and discovery routes
│   └── chat.py              # Chat messaging routes
├── templates/               # Jinja2 templates
│   ├── base.html           # Base template with navigation
│   ├── index.html          # Home page
│   ├── register.html       # User registration
│   ├── login.html          # User login
│   ├── discover.html       # User discovery page
│   ├── matches.html        # User matches page
│   ├── 404.html           # Error pages
│   └── 500.html
└── static/                 # Static assets
    ├── css/
    │   └── style.css       # Custom CSS
    └── js/
        └── main.js         # JavaScript functionality
```

## Quick Start

### Prerequisites
- Python 3.11+
- Flask and dependencies (see requirements.txt)

### Installation & Setup

1. **Environment Setup**: Ensure the `SESSION_SECRET` environment variable is set in Replit Secrets
2. **Install Dependencies**: Dependencies are automatically installed in Replit environment
3. **Database**: SQLite database is automatically created on first run

### Running the Application

The app runs automatically in Replit. Access it through the webview.

**Default port**: 5000  
**Database**: `matching_app.db` (SQLite, created automatically)

## Usage & Testing

### Basic Testing Steps

1. **Registration Flow**:
   - Navigate to `/register`
   - Create a new account with name, email, password
   - Should redirect to login page

2. **Login Flow**:
   - Use `/login` with registered credentials
   - Should redirect to home page with authenticated navigation

3. **Profile Management**:
   - Complete profile at `/profile/edit`
   - Add age, gender, bio, interests/tags, location
   - View profile at `/profile`

4. **Discovery & Matching**:
   - Visit `/discover` to see other users
   - Click "❤️ Like" on users you're interested in
   - When mutual likes occur, a match is created

5. **Chat Functionality**:
   - View matches at `/matches`
   - Click "💬 Chat" to message matched users
   - Send and receive messages (can be enhanced with real-time features)

### API Endpoints

#### Authentication
- `POST /register` - User registration
- `POST /login` - User login  
- `GET /logout` - User logout

#### Profiles
- `GET /profile` - View own profile
- `GET /profile/edit` - Edit profile form
- `POST /profile/edit` - Update profile
- `GET /profile/<user_id>` - View other user's profile

#### Matching
- `GET /discover` - Discover potential matches
- `POST /like/<user_id>` - Like a user
- `GET /matches` - View all matches

#### Chat
- `GET /chat/<match_id>` - Chat interface
- `POST /chat/<match_id>/send` - Send message

## Database Models

### User
- Authentication and core user data
- Relationships to Profile, Likes, Matches, Messages

### Profile  
- Detailed user information for matching
- Name, age, gender, bio, tags, location

### Like
- One-way likes between users
- Automatic match detection on mutual likes

### Match
- Mutual likes between two users
- Container for chat messages

### Message
- Chat messages between matched users
- Read status tracking

## Extension Points

This skeleton is designed for easy extension:

### Frontend Enhancements
- Replace TailwindCSS CDN with custom build
- Add image upload functionality  
- Implement real-time chat with WebSockets
- Add swipe-based UI components
- Progressive Web App (PWA) features

### Backend Enhancements  
- Advanced matching algorithms with compatibility scoring
- User reporting and moderation system
- Push notifications for matches and messages
- Location-based matching with geolocation
- Social media integration
- Premium features and subscriptions

### Infrastructure Upgrades
- PostgreSQL database migration
- Redis for session management and real-time features
- File storage integration for user photos
- Email verification system
- OAuth social login integration

## Security Features

- Password hashing with Werkzeug
- CSRF protection on all forms
- SQL injection protection via SQLAlchemy ORM
- Session management with Flask-Login
- Environment-based secret management

## Development Notes

### Code Organization
- **Blueprints**: Routes organized by functionality
- **Models**: Single file with all database models
- **Forms**: WTForms with comprehensive validation
- **Templates**: Jinja2 with template inheritance

### Database Design
- **Scalable**: Easy to migrate from SQLite to PostgreSQL
- **Normalized**: Proper foreign key relationships
- **Indexed**: Key fields indexed for performance
- **Extensible**: Easy to add new fields and relationships

### Error Handling
- Custom 404/500 error pages
- Form validation with user-friendly messages
- Database transaction rollback on errors
- Comprehensive logging for debugging

---

**Note**: This is a development skeleton. For production deployment, implement additional security measures, use a production WSGI server, and configure proper logging and monitoring.

## Support & Contributing

This skeleton provides a solid foundation for matching applications. Feel free to extend and customize based on your specific requirements!
