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

All endpoints except for login/register require JWT authentication via the Authorization header.

### Authentication

- `POST /api/auth/register` - Register a new matchmaker
  - Requires: name, email, password
  - Returns: matchmaker_id
  
- `POST /api/auth/login` - Login as a matchmaker and receive JWT token
  - Requires: email, password
  - Returns: token, matchmaker details
  
- `POST /api/auth/reset-password` - Request password reset
  - Requires: email
  - Returns: reset token (demo only)

### Users

- `POST /api/user` - Create a new user profile
  - Requires: detailed user profile data including personal, religious, background and lifestyle information
  - Returns: user_id
  
- `GET /api/user/<user_id>` - Get a specific user's profile
  - Returns: Complete user profile with personal, religious, background and lifestyle data
  
- `GET /api/matchmaker/users` - Get all users belonging to the authenticated matchmaker
  - Returns: List of users with basic information (id, name, email, gender, age, location)

### Matches

- `GET /api/user/<user_id>/matches` - Get matches for a specific user
  - Optional query param: limit (default: 10)
  - Returns: List of matches for the user with compatibility scores
  
- `GET /api/matches/all` - Get all top matches across the system (admin only)
  - Optional query params: limit_per_match (default: 5), min_score (default: 50)
  - Returns: List of all top matches across users
  
- `GET /api/matchmaker/matches` - Get matches for all applicants of the authenticated matchmaker
  - Optional query param: limit (default: 100)
  - Returns: List of matches for all applicants assigned to the matchmaker
  
- `GET /api/matches/compatibility/<user_a_id>/<user_b_id>` - Get detailed compatibility between two users
  - Returns: Compatibility score and detailed breakdown of compatibility factors

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