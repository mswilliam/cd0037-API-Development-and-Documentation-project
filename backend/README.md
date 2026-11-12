# Backend - Trivia API

The backend of the Trivia app: a Flask API backed by a PostgreSQL database through SQLAlchemy.

- `flaskr/__init__.py`: the application factory, the endpoints and the error handlers.
- `models.py`: the database connection and the `Question` and `Category` models.
- `test_flaskr.py`: the test suite.
- `trivia.psql`: the script that populates the development database.

## Setting up the Backend

### Install Dependencies

1. **Python 3.11 or later** - Follow the instructions to install the latest version of Python for your platform in the [Python docs](https://www.python.org/downloads/).

2. **Virtual Environment** - We recommend working within a virtual environment. This keeps the dependencies of each project separate and organized. From the `backend` folder:

```bash
python -m venv venv
source venv/bin/activate        # Mac / Linux
source venv/Scripts/activate    # Windows (Git Bash)
```

3. **PIP Dependencies** - With the virtual environment activated, install the dependencies:

```bash
python -m pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](https://flask.palletsprojects.com/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.
- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) are the Python SQL toolkit and ORM used to handle the database.
- [Flask-CORS](https://flask-cors.readthedocs.io/) is the extension used to handle cross-origin requests from the frontend server.
- [psycopg](https://www.psycopg.org/psycopg3/) is the PostgreSQL driver used by SQLAlchemy.

### Set up the Database

With PostgreSQL running, create the `trivia` database and populate it with the `trivia.psql` file. From the `backend` folder:

```bash
createdb -U postgres trivia
psql -U postgres -d trivia -f trivia.psql
```

To reset the database to its initial content, drop it and run the same commands again:

```bash
dropdb -U postgres trivia
```

#### Database credentials

The app connects to PostgreSQL with the user `postgres` and the password `password` by default.
These default values are only a convenience for local development: never use them for a real deployment.
To use other credentials, set these environment variables before running the app or the tests:

```bash
export DB_USER=postgres
export DB_PASSWORD='your_password'
export DB_HOST=localhost:5432
export DB_NAME=trivia            # development database
export TEST_DB_NAME=trivia_test  # test database
```

Use single quotes around the password: with double quotes, the shell would interpret special characters such as `$`.

### Run the Server

From the `backend` folder, with the virtual environment activated:

```bash
flask --app flaskr run --debug
```

The `--debug` flag enables the debugger and restarts the server automatically when a file changes. The API is available at `http://127.0.0.1:5000/`.

## API Reference

### Getting Started

- **Base URL:** this app can only be run locally. The backend is hosted at `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration.
- **Authentication:** this version of the application does not require authentication or API keys.
- **CORS:** cross-origin requests are allowed from any origin. Responses allow the `Content-Type` and `Authorization` headers and the `GET`, `POST`, `PUT`, `DELETE` and `OPTIONS` methods.
- **Request body:** requests with a body (`POST`, `PUT`) must send JSON, with the header `Content-Type: application/json`.

### Endpoints summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/categories` | List all categories |
| `GET` | `/questions?page={page}` | List questions, 10 per page, with all categories |
| `GET` | `/categories/{category_id}/questions` | List the questions of a category |
| `POST` | `/questions` | Create a question |
| `POST` | `/questions` (with `searchTerm`) | Search questions |
| `PUT` | `/questions/{question_id}` | Update a question |
| `DELETE` | `/questions/{question_id}` | Delete a question |
| `POST` | `/quizzes` | Get the next random question of a quiz |

### Error Handling

Errors are returned as JSON objects in the following format:

```json
{
  "success": false,
  "error": 404,
  "message": "resource not found"
}
```

The API returns the following error types:

| Status code | Message | Cause |
|---|---|---|
| 400 | `bad request` | The request is malformed or missing required data. |
| 404 | `resource not found` | The requested resource or page does not exist. |
| 405 | `method not allowed` | The HTTP method is not supported on this endpoint. |
| 422 | `unprocessable` | The request is well formed but could not be processed. |
| 500 | `internal server error` | An unexpected error occurred on the server. |

### Endpoints

#### `GET /categories`

- Fetches a dictionary of categories in which the keys are the ids and the values are the corresponding category names.
- Request arguments: none
- Returns: an object with a `success` value and a `categories` object of `id: category_string` key-value pairs.
- Errors: `405` if any other method than `GET` is used.
- Sample request: `curl http://127.0.0.1:5000/categories`

```json
{
  "success": true,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

#### `GET /questions`

- Fetches a paginated list of questions, the total number of questions, all categories and the current category.
- Request arguments:
  - `page` (integer, optional, default `1`): page number, starting from 1. Questions are returned in groups of 10.
- Returns: an object with a `success` value, the `questions` of the page, `totalQuestions`, a `categories` object of `id: category_string` pairs, and `currentCategory` (`null` when listing all questions).
- Errors: `404` if the page does not exist.
- Sample request: `curl http://127.0.0.1:5000/questions?page=1`

```json
{
  "success": true,
  "questions": [
    {
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?",
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4
    }
  ],
  "totalQuestions": 19,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "currentCategory": null
}
```

#### `GET /categories/{category_id}/questions`

- Fetches the questions of the given category.
- Path parameters:
  - `category_id` (integer, required): id of the category.
- Request arguments:
  - `page` (integer, optional, default `1`): page number. Questions are returned in groups of 10.
- Returns: an object with a `success` value, the `questions` of the category, `totalQuestions` (number of questions in the category) and `currentCategory` (name of the category). A category without questions returns an empty list.
- Errors: `404` if the category does not exist, or if the page does not exist.
- Sample request: `curl http://127.0.0.1:5000/categories/1/questions`

```json
{
  "success": true,
  "questions": [
    {
      "id": 20,
      "question": "What is the heaviest organ in the human body?",
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4
    }
  ],
  "totalQuestions": 3,
  "currentCategory": "Science"
}
```

#### `POST /questions` (create a question)

- Creates a new question.
- Request body:
  - `question` (string, required): text of the question.
  - `answer` (string, required): text of the answer.
  - `difficulty` (integer from 1 to 5, required).
  - `category` (integer, required): id of an existing category.

  Numeric values sent as strings (for example `"3"`) are accepted.
- Returns: status `201` and an object with a `success` value and the id of the created question.
- Errors: `400` if a field is missing, empty or invalid, `422` if the category does not exist or the question cannot be saved.
- Sample request:

```bash
curl -X POST http://127.0.0.1:5000/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the capital of Luxembourg?", "answer": "Luxembourg", "difficulty": 2, "category": 3}'
```

```json
{
  "success": true,
  "created": 24
}
```

#### `POST /questions` (search questions)

- Searches the questions whose text contains the search term (case-insensitive substring match). The same endpoint creates a question when the body has no `searchTerm` key.
- Request body:
  - `searchTerm` (string, required): the term to look for.
- Request arguments:
  - `page` (integer, optional, default `1`): page number. Questions are returned in groups of 10.
- Returns: an object with a `success` value, the matching `questions`, `totalQuestions` (number of matching questions) and `currentCategory` (`null`). A search without results returns an empty list.
- Errors: `400` if `searchTerm` is not a string.
- Sample request:

```bash
curl -X POST http://127.0.0.1:5000/questions \
  -H "Content-Type: application/json" \
  -d '{"searchTerm": "title"}'
```

```json
{
  "success": true,
  "questions": [
    {
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2
    },
    {
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?",
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3
    }
  ],
  "totalQuestions": 2,
  "currentCategory": null
}
```

#### `PUT /questions/{question_id}`

- Updates the question with the given id. All the fields are replaced, so the body must contain all of them, even those that do not change.
- Path parameters:
  - `question_id` (integer, required): id of the question to update.
- Request body: same fields and rules as for creating a question.
  - `question` (string, required): text of the question.
  - `answer` (string, required): text of the answer.
  - `difficulty` (integer from 1 to 5, required).
  - `category` (integer, required): id of an existing category.

  Numeric values sent as strings (for example `"3"`) are accepted.
- Returns: an object with a `success` value, the id of the updated question and the updated `question` object, as saved in the database.
- Errors: `404` if the question does not exist, `400` if a field is missing, empty or invalid, `422` if the category does not exist or the question cannot be saved.
- Sample request:

```bash
curl -X PUT http://127.0.0.1:5000/questions/20 \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the heaviest internal organ in the human body?", "answer": "The Liver", "difficulty": 3, "category": 1}'
```

```json
{
  "success": true,
  "updated": 20,
  "question": {
    "id": 20,
    "question": "What is the heaviest internal organ in the human body?",
    "answer": "The Liver",
    "category": 1,
    "difficulty": 3
  }
}
```


#### `DELETE /questions/{question_id}`

- Deletes the question with the given id.
- Path parameters:
  - `question_id` (integer, required): id of the question to delete.
- Returns: an object with a `success` value and the id of the deleted question.
- Errors: `404` if the question does not exist, `422` if it cannot be deleted.
- Sample request: `curl -X DELETE http://127.0.0.1:5000/questions/23`

```json
{
  "success": true,
  "deleted": 23
}
```

#### `POST /quizzes`

- Fetches a random question to play the quiz, within the given category and excluding the questions already asked.
- Request body:
  - `previous_questions` (list of integers, required): ids of the questions already asked. Can be empty.
  - `quiz_category` (object, required): the category to play, as `{"type": <string>, "id": <integer or string>}`. An `id` of `0` means all categories (the `type` is ignored).
- Returns: an object with a `success` value and a `question` object. When no question is left in the category, `question` is `null`, which ends the game.
- Errors: `400` if the body is missing or invalid, `404` if the category does not exist.
- Sample request:

```bash
curl -X POST http://127.0.0.1:5000/quizzes \
  -H "Content-Type: application/json" \
  -d '{"previous_questions": [20], "quiz_category": {"type": "Science", "id": "1"}}'
```

```json
{
  "success": true,
  "question": {
    "id": 22,
    "question": "Hematology is a branch of medicine involving the study of what?",
    "answer": "Blood",
    "category": 1,
    "difficulty": 4
  }
}
```

## Testing

The test suite uses `unittest` and covers the success and error behaviors of every endpoint, as well as the error handlers and the CORS headers.

Create the test database once:

```bash
createdb -U postgres trivia_test
```

Then run the tests from the `backend` folder, with the virtual environment activated:

```bash
python test_flaskr.py
```

Each test starts from a clean state: the tables are created and seeded with a known set of categories and questions in `setUp`, then dropped in `tearDown`. You do not need to load `trivia.psql` into the test database.

### Code style

The backend code follows [PEP 8](https://peps.python.org/pep-0008/). To check it:

```bash
python -m pip install flake8
python -m flake8 flaskr/__init__.py models.py test_flaskr.py
```
