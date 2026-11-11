# Udacity Trivia App

A full-stack trivia game for the Udacity community. Players can browse questions by category, add and delete questions, search them, and play a quiz on all categories or on a single one.

The project was built for the *API Development and Documentation* course. The React frontend was provided; the work consisted of designing, implementing, testing and documenting the Flask API that powers it, using test-driven development.

The application lets users:

1. Display questions, either all questions or by category. Questions show the question, category and difficulty rating by default, and can show or hide the answer.
2. Delete questions.
3. Add questions, which require the question and answer text, a category and a difficulty.
4. Search for questions based on a text query string.
5. Play the quiz game, with random questions from all categories or from a specific category.

## Project structure

- [`backend`](./backend/README.md): the Flask API, its PostgreSQL models and its test suite.
- [`frontend`](./frontend/README.md): the React application that consumes the API.

## Code style

The backend follows [PEP 8](https://peps.python.org/pep-0008/), checked with `flake8`. Please keep to these guidelines if you contribute to the project.

## Getting Started

### Prerequisites

- **Python 3.11** or later
- **PostgreSQL** (tested with version 18)
- **Node.js** and `npm`
- **Git**

> **Windows users:** the commands below are written for **Git Bash**. The virtual environment is activated with `source venv/Scripts/activate` instead of `source venv/bin/activate`.

### 1. Set up the database

From the `backend` folder:

```bash
createdb -U postgres trivia
psql -U postgres -d trivia -f trivia.psql
createdb -U postgres trivia_test
```

The app connects with the user `postgres` and the password `password` by default. To use other credentials, set environment variables before running the backend or the tests:

```bash
export DB_PASSWORD='your_password'
```

See the [backend README](./backend/README.md#database-credentials) for all the available variables.

### 2. Run the backend

From the `backend` folder:

```bash
python -m venv venv
source venv/bin/activate        # Windows (Git Bash): source venv/Scripts/activate
python -m pip install -r requirements.txt
flask --app flaskr run --debug
```

The API runs on `http://127.0.0.1:5000/`.

### 3. Run the frontend

In a second terminal, from the `frontend` folder:

```bash
npm install                                     # only once, to install the dependencies
export NODE_OPTIONS=--openssl-legacy-provider   # required with Node.js 17 or later
npm start
```

The app opens on `http://localhost:3000` and forwards API requests to the backend through the proxy defined in `package.json`.

> `NODE_OPTIONS` is needed because this React project uses an older version of webpack: without it, recent versions of Node.js stop `npm start` with the error `ERR_OSSL_EVP_UNSUPPORTED`. The variable only lasts for the current terminal session.

Both servers must run at the same time.

## Tests

From the `backend` folder, with the virtual environment activated. If you use custom database credentials, export them in this terminal too, as environment variables only apply to the terminal where they are set:

```bash
python test_flaskr.py
```

The 28 tests cover the success and error behaviors of every endpoint, the error handlers and the CORS headers. Each test runs on the `trivia_test` database, seeded with a known set of data and cleaned after each test, so the tests never touch the development data. See the [backend README](./backend/README.md#testing) for details.

## API Reference

The full API documentation (base URL, error handling, every endpoint with its parameters, a sample request and a sample response) is in the [backend README](./backend/README.md#api-reference).

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/categories` | List all categories |
| `GET` | `/questions?page={page}` | List questions, 10 per page, with all categories |
| `GET` | `/categories/{category_id}/questions` | List the questions of a category |
| `POST` | `/questions` | Create a question |
| `POST` | `/questions` (with `searchTerm`) | Search questions |
| `DELETE` | `/questions/{question_id}` | Delete a question |
| `POST` | `/quizzes` | Get the next random question of a quiz |

## Changes to the starter code

- **Response keys:** the API returns `totalQuestions` and `currentCategory` (camelCase), as required by the API contract. `frontend/src/components/QuestionView.js` was updated to read these keys instead of `total_questions` and `current_category`.
- **Data model:** `Question.category` is declared as an integer foreign key to `categories.id`, matching the schema created by `trivia.psql`. The starter model declared it as a string.
- **Database credentials** are read from environment variables, with the original values as defaults, so that no password is stored in the repository.

The game mechanics are unchanged: a quiz has up to five questions, and ends earlier when no question is left in the chosen category.

## Deployment

Not applicable: this version of the app is only run locally.

## Authors

- MANGOUA SOFACK William: backend API, error handlers, test suite and documentation.
- Udacity: frontend, data models and database script provided as starter code.

## Acknowledgements

Thanks to the Udacity team and to the instructors of the *API Development and Documentation* course for the project and its guidance.
