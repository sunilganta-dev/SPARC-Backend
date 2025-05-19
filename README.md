# SPARC - Shidduch Programming and Relationship Compatibility

SPARC is a backend system for a shidduch (Jewish matchmaking) program. It provides an algorithm to match users based on their profiles and preferences.

## Features

- User profile management with detailed attributes
- Advanced matching algorithm based on weighted compatibility scores
- Authentication system for matchmakers
- API endpoints for retrieving matches and user data
- Configurable matching parameters

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SPARC.git
cd SPARC-Backend
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export DATABASE_URL=postgresql://username:password@localhost/shidduch
export SECRET_KEY=your_secret_key
export ADMIN_EMAIL=your_admin_email@example.com
```

5. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Running the Application

```bash
python run.py
```

The API will be available at http://localhost:5000

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new matchmaker
- `POST /api/auth/login` - Login as a matchmaker and receive JWT token
- `POST /api/auth/reset-password` - Request password reset

### Users

- `POST /api/user` - Create a new user profile
- `GET /api/user/<user_id>` - Get a specific user's profile
- `GET /api/matchmaker/users` - Get all users belonging to the authenticated matchmaker

### Matches

- `GET /api/user/<user_id>/matches` - Get matches for a specific user
- `GET /api/matches/all` - Get all top matches across the system (admin only)
- `GET /api/matchmaker/matches` - Get matches for all applicants of the authenticated matchmaker
- `GET /api/matches/compatibility/<user_a_id>/<user_b_id>` - Get detailed compatibility between two users

## Matching Algorithm

The matching algorithm considers various factors from user profiles, including:

- Religious observance (Shabbat, Kosher, etc.)
- Cultural background
- Age and height preferences
- Family plans and values
- Lifestyle preferences
- Communication styles

Each factor is assigned a weight in the compatibility calculation, which can be customized in the `match_engine.py` file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.