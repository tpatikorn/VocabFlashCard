# Vocabulary Learning Flask Webapp - Requirements Specification

## 1. Overview

This document outlines the requirements for a Flask-based web application designed to help users learn vocabulary through adaptive practice sessions. The application will utilize a collection of IELTS vocabulary words organized into thematic groups, with an adaptive difficulty system that adjusts based on user performance.

## 2. System Features

### 2.1 User Authentication
- Google OAuth integration for user login (already implemented in templates/base.html)
- User session management
- User profile display with name and profile picture

### 2.2 User Dashboard
- Display of user statistics:
  - Number of words answered correctly in the past week
  - Total words practiced
  - Overall accuracy rate
  - Performance by word group
  - Learning streaks/consistency metrics
- Navigation to practice sessions

### 2.3 Practice Sessions
- Adaptive difficulty system based on user performance:
  - Level 0: 4 choices with both English and Thai meanings, antonyms/synonyms as hints, no time limit
  - Level 1: 4 choices with both English and Thai meanings, 1-minute time limit per word
  - Level 2: 4 choices with only English meanings, 1-minute time limit per word
  - Level 3+: One additional choice and 5 seconds less time per level (e.g., Level 3 = 5 choices, 55 seconds)
- Word progression system:
  - Correct answer: Word level increases by 1
  - Incorrect answer: Word level decreases by 1 (minimum level 0)
- Distractor selection:
  - Incorrect options pulled from the same word group
  - Distractors should have similarity to correct answer (same part of speech, related meaning)
- Session management:
  - 20-minute global timer that runs continuously once started
  - Session ends immediately when time expires, even if in the middle of a word
  - Timer cannot be paused or resumed

### 2.4 Scoring System
- Points calculated as (word level + 1) for each correct answer:
  - Level 0 word correct = 1 point
  - Level 1 word correct = 2 points
  - Level 2 word correct = 3 points
  - And so on...
- Session score displayed at the end of each practice session

### 2.5 Data Management
- Persistent storage of user progress:
  - Track word levels per user across sessions
  - Store user statistics and performance metrics
  - Maintain word group performance data

## 3. Data Structure

### 3.1 Vocabulary Data
- Vocabulary words organized in JSON files by thematic groups
- Each word entry contains:
  - Word and part of speech
  - English and Thai meanings
  - Example sentences
  - Synonyms and antonyms
  - Word forms
  - Difficulty tier and frequency information

### 3.2 User Data
- User identification via Google OAuth
- Per-word level tracking for each user
- Session history and performance statistics
- Group-based performance metrics

## 4. Technical Requirements

### 4.1 Backend
- Flask web framework
- Google OAuth integration (as implemented in base.html)
- Database for user progress and statistics (SQLite, PostgreSQL, or similar)
- JSON parsing for vocabulary data

### 4.2 Frontend
- HTML templates extending base.html
- Responsive design using Bootstrap (already included in base.html)
- JavaScript for interactive elements and timer functionality
- AJAX for dynamic content updates where appropriate

### 4.3 Data Storage
- Persistent storage solution for:
  - User progress (word levels)
  - User statistics
  - Session history
- Data schema to efficiently track:
  - User-word relationships and levels
  - Practice session results
  - Performance metrics over time

## 5. User Interface Requirements

### 5.1 Main Dashboard
- Google login button (when not logged in)
- User profile display (when logged in)
- Statistics summary
- Link to start practice session

### 5.2 Practice Interface
- Clear display of current word
- Multiple choice options based on current difficulty level
- Visual timer for timed questions
- Progress indicator
- Score tracking during session
- Clear feedback on answer correctness

## 6. Performance Requirements

### 6.1 Responsiveness
- Page load times under 2 seconds
- Practice session transitions under 1 second

### 6.2 Scalability
- Support for multiple concurrent users
- Efficient database queries for user statistics
- Caching mechanisms for vocabulary data where appropriate

## 7. Security Requirements

### 7.1 Authentication
- Secure Google OAuth implementation
- Protection against session hijacking
- Proper session timeout handling

### 7.2 Data Protection
- Sanitization of user inputs
- Protection against injection attacks
- Secure storage of user data

## 8. Future Enhancement Opportunities

### 8.1 Additional Features
- Custom vocabulary groups
- Progress comparison with other users
- Achievement badges
- Mobile-responsive design improvements
- Export functionality for user progress

### 8.2 Analytics
- Detailed performance insights
- Learning curve visualization
- Group-based difficulty adjustments

## 9. Assumptions and Dependencies

### 9.1 Assumptions
- Users have access to modern web browsers
- Google OAuth service availability
- Vocabulary data will remain relatively static

### 9.2 Dependencies
- Flask framework
- Google OAuth client library
- Bootstrap CSS framework (already included)
- Database management system

## 10. Acceptance Criteria

### 10.1 Functional Criteria
- Users can successfully log in with Google
- Users can view their statistics dashboard
- Users can complete practice sessions with adaptive difficulty
- Word levels are correctly tracked and persisted
- Scoring system works as specified
- Session timer functions correctly

### 10.2 Non-Functional Criteria
- Application loads and responds within specified time limits
- User data is securely stored and managed
- Interface is responsive and user-friendly