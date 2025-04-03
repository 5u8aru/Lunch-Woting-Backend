# Lunch Voting System

A Django-based application for voting which restaurant to chose today.

## Features

- **User Registration**: Users can register and authenticate using JWT tokens.
- **Restaurant Management**: Add and view restaurants.
- **Menu Management**: Add and view menus for specific restaurants on specific days.
- **Voting System**: Users can vote for restaurants based on their menus.
- **API Versioning**: Supports different voting logic based on API version.

## Requirements

- Docker
- Docker Compose

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/5u8aru/Lunch-Woting-Backend
   cd Lunch-Woting-Backend
   ```

2. Build and start the services:
   ```bash
   docker-compose up --build
   ```

3. Apply migrations (if not automated):
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. Access the application:
   - **API**: `http://localhost:8000`
   - **Admin Panel**: `http://localhost:8000/admin`

## API Endpoints

### Authentication

- **Obtain Token**: `POST /api/auth/token/`
  ```json
  {
      "username": "testuser",
      "password": "testpassword"
  }
  ```

- **Refresh Token**: `POST /api/auth/token/refresh/`
  ```json
  {
      "refresh": "<refresh_token>"
  }
  ```

### Users

- **Register**: `POST /api/users/register/`
  ```json
  {
      "username": "testuser",
      "email": "testuser@example.com",
      "password": "testpassword"
  }
  ```

### Restaurants

- **List Restaurants**: `GET /api/restaurants/`
- **Add Restaurant**: `POST /api/restaurants/`

### Menus

- **List Today's Menu for a Restaurant**: `GET /api/restaurants/<restaurant_id>/menus/`
- **Add Menu for a Restaurant**: `POST /api/restaurants/<restaurant_id>/menus/`

### Votes

- **Vote for a Restaurant**:
  - API Version 1: `POST /api/votes/` (requires `restaurant` and `day_of_week`)
  - API Version 2: `POST /api/votes/` (requires only `restaurant`)
- **Get Today's Voting Results**: `GET /api/votes/`
- **Delete All Votes**: `DELETE /api/votes/delete_all/`

## Running Tests

1. Run all tests:
   ```bash
   pytest
   ```

2. Run tests with coverage:
   ```bash
   pytest --cov=app --cov-report=term-missing
   ```

## Environment Variables

The following environment variables can be configured in the `docker-compose.yml` file:

- `POSTGRES_USER`: PostgreSQL username (default: `postgres`)
- `POSTGRES_PASSWORD`: PostgreSQL password (default: `postgres`)
- `POSTGRES_DB`: PostgreSQL database name (default: `lunch_voting`)
- `POSTGRES_HOST`: PostgreSQL host (default: `db`)
- `POSTGRES_PORT`: PostgreSQL port (default: `5432`)
- `DJANGO_DEBUG`: Django debug mode (default: `True`)

## Development

1. Install dependencies locally:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the development server:
   ```bash
   python manage.py runserver
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```