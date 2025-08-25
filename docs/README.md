# Vocabulary Learning Flask Webapp

A Flask-based web application designed to help users learn vocabulary through adaptive practice sessions. The application utilizes a collection of IELTS vocabulary words organized into thematic groups, with an adaptive difficulty system that adjusts based on user performance.

## Features

- Google OAuth authentication
- User dashboard with comprehensive statistics
- Adaptive practice sessions with difficulty levels:
  - Level 0: 4 choices with both English and Thai meanings, hints, no time limit
  - Level 1: 4 choices with both English and Thai meanings, 1-minute time limit
  - Level 2: 4 choices with only English meanings, 1-minute time limit
  - Level 3+: One additional choice and 5 seconds less time per level
- Word progression system based on correct/incorrect answers
- 20-minute practice sessions with global timer
- Detailed performance tracking and statistics
- Synonym matching game with drag-and-drop interface

## Prerequisites

- Python 3.7+
- PostgreSQL database
- Google OAuth credentials

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd VocabFlashCard
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Create a PostgreSQL database
   - Run the `init.sql` script to create the necessary tables:
     ```
     psql -U your_username -d your_database -f docs/init.sql
     ```

5. Configure environment variables:
   - Copy `.env.example` to `.env`:
     ```
     cp .env.example .env
     ```
   - Update the values in `.env` with your actual configuration:
     ```
     SECRET_KEY=your_secret_key_here
     DB_SERVER=your_db_server
     DB_PORT=5432
     DB_USER=your_db_user
     DB_PASS=your_db_password
     DB_DB=your_database_name
     GOOGLE_CLIENT_ID=your_google_client_id
     GOOGLE_CLIENT_SECRET=your_google_client_secret
     ```

6. Load vocabulary data:
   - The vocabulary JSON files in the `docs/vocab/` directory will be automatically loaded by the application

## Running the Application

1. Activate the virtual environment:
   ```
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Run the Flask application:
   ```
   python app.py
   ```

3. Open your browser and navigate to `http://localhost:8087/flash_card/`

## Project Structure

```
VocabFlashCard/
├── app.py                 # Main Flask application
├── init.sql               # Database initialization script
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
├── README.md              # This file
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Landing page
│   ├── dashboard.html     # User dashboard
│   ├── practice.html      # Practice session page
│   └── synonym_game.html  # Synonym matching game
├── vocab/                 # Vocabulary JSON files
│   ├── IELTS_Group_Arts_Entertainment.json
│   ├── IELTS_Group_Economy_Finance.json
│   └── ...                # Additional vocabulary files
├── static/                # Static assets (CSS, JS, images)
│   ├── css/
│   │   └── synonym_game.css  # Styles for synonym game
│   └── js/
├── manager/               # Application managers
│   ├── __init__.py        # Package initializer
│   ├── database_manager.py# Database connection management
│   ├── user_manager.py    # User-related operations
│   ├── vocabulary_manager.py # Vocabulary data management
│   ├── word_manager.py    # Word-related database operations
│   ├── user_word_level_manager.py # User word level tracking
│   ├── practice_session_manager.py # Practice session management
│   ├── user_progress_manager.py # User progress tracking
│   ├── user_statistics_manager.py # User statistics management
│   ├── auth_manager.py    # Authentication management
│   ├── practice_manager.py # Practice functionality management
│   ├── synonym_game_manager.py # Synonym game management
│   └── flash_card_blueprint.py # Flask blueprint for flash card APIs
└── ...
```

## Database Schema

The application uses a PostgreSQL database with the following tables:

- `users`: Stores user information from Google OAuth
- `word_groups`: Vocabulary groups (e.g., "Education & Learning")
- `words`: Individual vocabulary words with meanings and examples
- `user_word_levels`: Tracks each user's level for each word
- `practice_sessions`: Records practice session information
- `user_progress`: Tracks individual word attempts during sessions
- `user_statistics`: Aggregated user statistics for faster queries
- `synonyms`: Synonym data for the synonym game
- `synonym_games`: Tracks synonym game sessions
- `synonym_scores`: Tracks scores for each round of a synonym game

## Adaptive Difficulty System

The application implements an adaptive difficulty system:

1. Each word starts at level 0 for each user
2. Correct answers increase the word level by 1
3. Incorrect answers decrease the word level by 1 (minimum level 0)
4. Difficulty levels:
   - Level 0: 4 choices with both English and Thai meanings, hints, no time limit
   - Level 1: 4 choices with both English and Thai meanings, 1-minute time limit
   - Level 2: 4 choices with only English meanings, 1-minute time limit
   - Level 3+: One additional choice and 5 seconds less time per level
5. Distractors (incorrect choices) are selected from the same word group with similarity to the correct answer

## Scoring System

- Points are calculated as (word level + 1) for each correct answer
- Level 0 word correct = 1 point
- Level 1 word correct = 2 points
- Level 2 word correct = 3 points
- And so on...

## Synonym Game

The synonym matching game features:

1. Drag-and-drop interface for matching words to their meanings
2. Two meanings displayed in separate boxes
3. Word pills that can be dragged to the correct meaning box
4. Visual feedback with color-coded results (green for correct, red for incorrect)
5. 5 rounds per game or until 5 minutes elapse
6. Scoring based on percentage of correct words per meaning (max 1000 points)

## API Endpoints

All endpoints are under the `/flash_card` prefix:

- `GET /flash_card/` - Landing page
- `GET /flash_card/dashboard` - User dashboard with statistics
- `GET /flash_card/practice` - Practice session page
- `GET /flash_card/synonym-game` - Synonym game page
- `GET /flash_card/auth/login` - Google OAuth login
- `GET /flash_card/auth/callback` - Google OAuth callback
- `GET /flash_card/auth/logout` - Logout user
- `POST /flash_card/api/start_session` - Start a new practice session
- `POST /flash_card/api/end_session` - End the current practice session
- `GET /flash_card/api/next_word` - Get the next word for practice
- `POST /flash_card/api/submit_answer` - Submit an answer and update user progress
- `POST /flash_card/api/synonym-game/start` - Start a new synonym game
- `GET /flash_card/api/synonym-game/next-round` - Get the next round of the synonym game
- `POST /flash_card/api/synonym-game/submit-round` - Submit answers for a round of the synonym game
- `POST /flash_card/api/synonym-game/end` - End the current synonym game

## Google OAuth Configuration

To configure Google OAuth:

1. Create a project in the Google Cloud Console
2. Enable the Google+ API
3. Create OAuth 2.0 credentials (Client ID and Client Secret)
4. Add authorized redirect URIs:
   - `http://localhost:8087/flash_card/auth/callback` (for local development)
5. Update the `.env` file with your Google OAuth credentials

## Development

To contribute to this project:

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.