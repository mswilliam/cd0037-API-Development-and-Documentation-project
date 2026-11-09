# Backend - Trivia API

## Setting up the Backend

### Install Dependencies

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### Set up the Database

With Postgres running, create a `trivia` database:

```bash
createdb trivia
```

Populate the database using the `trivia.psql` file provided. From the `backend` folder in terminal run:

```bash
psql trivia < trivia.psql
```

#### Database credentials

The app connects to PostgreSQL with the user `postgres` and the password `password` by default.
To use other credentials, set these environment variables before running the app or the tests:

```bash
export DB_USER=postgres
export DB_PASSWORD='your_password'
export DB_HOST=localhost:5432
export DB_NAME=trivia            # development database
export TEST_DB_NAME=trivia_test  # test database
```

### Run the Server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## To Do Tasks

These are the files you'd want to edit in the backend:

1. `backend/flaskr/__init__.py`
2. `backend/test_flaskr.py`

One note before you delve into your tasks: for each endpoint, you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.
2. Create an endpoint to handle `GET` requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
3. Create an endpoint to handle `GET` requests for all available categories.
4. Create an endpoint to `DELETE` a question using a question `ID`.
5. Create an endpoint to `POST` a new question, which will require the question and answer text, category, and difficulty score.
6. Create a `POST` endpoint to get questions based on category.
7. Create a `POST` endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
8. Create a `POST` endpoint to get questions to play the quiz. This endpoint should take a category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
9. Create error handlers for all expected errors including 400, 404, 422, and 500.

## Documenting your Endpoints

You will need to provide detailed documentation of your API endpoints including the URL, request parameters, and the response body. Use the example below as a reference.

### Documentation Example

`GET '/api/v1.0/categories'`

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, `categories`, that contains an object of `id: category_string` key: value pairs.

```json
{
  "1": "Science",
  "2": "Art",
  "3": "Geography",
  "4": "History",
  "5": "Entertainment",
  "6": "Sports"
}
```

## API Reference

### Getting Started

- **Base URL:** this app can only be run locally. The backend is hosted at `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration.
- **Authentication:** this version of the application does not require authentication or API keys.
- **CORS:** cross-origin requests are allowed from any origin. Responses allow the `Content-Type` and `Authorization` headers and the `GET`, `POST`, `DELETE` and `OPTIONS` methods.

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

## Testing

Write at least one test for the success and at least one error behavior of each endpoint using the unittest library.

To deploy the tests,

Create the test database once, run:

```bash
createdb trivia_test
```

Then run the tests from the `backend` folder:

```bash
python test_flaskr.py
```

Each test starts from a clean state: the tables are created and seeded with a known set of categories and questions in `setUp`, then dropped in `tearDown`. You do not need to reload `trivia.psql` before running the tests.
