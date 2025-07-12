import pytest
from unittest.mock import patch
from app.models import (
    read_all_active_students,
    read_student_by_id,
    create_student,
    update_student,
    archive_student,
    read_students_by_ids,
)
from app.services import (
    get_all_active_students,
    get_student_by_id,
    create_students,
    update_students,
    archive_students,
)

# =======================
# Fixtures
# =======================


@pytest.fixture
def valid_student_create_data():
    return [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "is_international": False,
        },
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "janedoe@example.com",
            "is_international": True,
        },
    ]


@pytest.fixture
def valid_student_update_data():
    return [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "is_international": False,
        }
    ]


@pytest.fixture
def student_missing_id(valid_student_update_data):
    # Return a version of update data without 'id'
    data = [item.copy() for item in valid_student_update_data]
    for d in data:
        d.pop("id", None)
    return data


@pytest.fixture
def valid_student_ids():
    return [1, 2]


# =======================
# DB Mocks
# =======================


@pytest.fixture
def mock_db_read_all():
    with patch("app.services.student.read_all_active_students") as mock:
        yield mock


@pytest.fixture
def mock_db_read_one():
    with patch("app.services.student.read_student_by_id") as mock:
        yield mock


@pytest.fixture
def mock_db_read_many():
    with patch("app.services.student.read_students_by_ids") as mock:
        yield mock


@pytest.fixture
def mock_db_create():
    with patch("app.services.student.create_student") as mock:
        yield mock


@pytest.fixture
def mock_db_update():
    with patch("app.services.student.update_student") as mock:
        yield mock


@pytest.fixture
def mock_db_archive():
    with patch("app.services.student.archive_student") as mock:
        yield mock


# =======================
# Service Tests
# =======================


def test_get_all_active_students(mock_db_read_all):
    mock_db_read_all.return_value = [
        (
            1,
            "John",
            "Doe",
            "a@a.com",
            "123 Main St",
            "Anytown",
            "ON",
            "Canada",
            "local",
            "active",
            0,
            0,
            1,
            "2024-01-01",
            "2024-01-01",
            0,
        )
    ]
    students = get_all_active_students()
    assert len(students) == 1
    assert students[0]["first_name"] == "John"
    mock_db_read_all.assert_called_once()


def test_get_all_active_students_none(mock_db_read_all):
    mock_db_read_all.return_value = None
    with pytest.raises(RuntimeError):
        get_all_active_students()


def test_get_student_by_id(mock_db_read_one):
    mock_db_read_one.return_value = (
        1,
        "John",
        "Doe",
        "a@a.com",
        "123 Main St",
        "Anytown",
        "ON",
        "Canada",
        "local",
        "active",
        0,
        0,
        1,
        "2024-01-01",
        "2024-01-01",
        0,
    )
    student = get_student_by_id(1)
    assert student["first_name"] == "John"
    mock_db_read_one.assert_called_once_with(1)


def test_get_student_by_id_not_found(mock_db_read_one):
    mock_db_read_one.return_value = None
    student = get_student_by_id(123)
    assert student is None


def test_create_students(mock_db_create, mock_db_read_many, valid_student_create_data):
    mock_db_create.side_effect = [1, 2]
    mock_db_read_many.return_value = [
        (
            1,
            "John",
            "Doe",
            "johndoe@example.com",
            None,
            None,
            None,
            None,
            "local",
            "active",
            0,
            False,
            None,
            "2024-07-12",
            "2024-07-12",
            0,
        ),
        (
            2,
            "Jane",
            "Doe",
            "janedoe@example.com",
            None,
            None,
            None,
            None,
            "local",
            "active",
            0,
            True,
            None,
            "2024-07-12",
            "2024-07-12",
            0,
        ),
    ]

    created, error = create_students(valid_student_create_data)

    assert error is None
    assert len(created) == 2
    assert mock_db_create.call_count == 2
    mock_db_read_many.assert_called_once_with([1, 2])


def test_create_students_failure(
    mock_db_create, mock_db_read_many, valid_student_create_data
):
    mock_db_create.side_effect = [None, None]
    created, error = create_students(valid_student_create_data)

    assert created == []
    assert error is None
    mock_db_read_many.assert_not_called()


def test_update_students(mock_db_update, mock_db_read_many, valid_student_update_data):
    mock_db_update.return_value = 1
    mock_db_read_many.return_value = [
        (
            1,
            "John",
            "Doe",
            "john@example.com",
            None,
            None,
            None,
            None,
            "local",
            "active",
            0,
            False,
            None,
            "2024-07-12",
            "2024-07-12",
            0,
        )
    ]

    updated, error = update_students(valid_student_update_data)

    assert error is None
    assert len(updated) == 1
    assert mock_db_update.call_count == 1
    mock_db_read_many.assert_called_once_with([1])


def test_update_students_no_success(
    mock_db_update, mock_db_read_many, valid_student_update_data
):
    mock_db_update.return_value = 0
    updated, error = update_students(valid_student_update_data)

    assert updated == []
    assert error is None
    mock_db_update.assert_called_once()
    mock_db_read_many.assert_not_called()


def test_update_students_missing_id(
    mock_db_update, mock_db_read_many, student_missing_id
):
    updated, error = update_students(student_missing_id)

    assert updated == []
    assert error is None
    mock_db_update.assert_not_called()
    mock_db_read_many.assert_not_called()


def test_archive_students(mock_db_archive, valid_student_ids):
    mock_db_archive.side_effect = [1, 1]
    archived = archive_students(valid_student_ids)

    assert len(archived) == 2
    assert mock_db_archive.call_count == 2


def test_archive_students_none_archived(mock_db_archive, valid_student_ids):
    mock_db_archive.return_value = 0
    archived = archive_students(valid_student_ids)

    assert archived == []


def test_archive_students_invalid_ids():
    with pytest.raises(ValueError):
        archive_students(["one", 2])


# =======================
# Model Tests
# =======================


@patch("app.models.student.db.execute_query")
def test_read_all_active_students(mock_execute):
    mock_execute.return_value = [("mocked",)]
    result = read_all_active_students()
    assert result == [("mocked",)]
    mock_execute.assert_called_once_with(
        "SELECT * FROM students WHERE status = 'active';"
    )


@patch("app.models.student.db.execute_query")
def test_read_student_by_id_found(mock_execute):
    mock_execute.return_value = [("student_1",)]
    result = read_student_by_id(1)
    assert result == ("student_1",)
    mock_execute.assert_called_once_with("SELECT * FROM students WHERE id = ?;", (1,))


@patch("app.models.student.db.execute_query")
def test_read_student_by_id_not_found(mock_execute):
    mock_execute.return_value = []
    result = read_student_by_id(999)
    assert result is None
    mock_execute.assert_called_once()


@patch("app.models.student.db.execute_query")
def test_read_students_by_ids_empty_list(mock_execute):
    result = read_students_by_ids([])
    assert result == []
    mock_execute.assert_not_called()


@patch("app.models.student.db.execute_query")
def test_read_students_by_ids_success(mock_execute):
    mock_execute.return_value = [("s1",), ("s2",)]
    result = read_students_by_ids([1, 2])

    assert result == [("s1",), ("s2",)]
    mock_execute.assert_called_once()
    assert "IN (?,?)" in mock_execute.call_args.args[0]
    assert mock_execute.call_args.args[1] == [1, 2]


@patch("app.models.student.db.execute_query")
def test_create_student_success(mock_execute):
    mock_cursor = type("MockCursor", (), {"lastrowid": 10})()
    mock_execute.return_value = mock_cursor

    params = (
        "John",
        "Doe",
        "j@example.com",
        None,
        None,
        None,
        None,
        "local",
        "active",
        0,
        False,
        None,
    )
    result = create_student(params)

    assert result == 10
    mock_execute.assert_called_once()

    query, called_params = mock_execute.call_args.args
    assert "INSERT INTO students" in query
    assert called_params == params


@patch("app.models.student.db.execute_query")
def test_create_student_failure(mock_execute):
    mock_execute.return_value = None
    result = create_student(("bad",))
    assert result is None


@patch("app.models.student.db.execute_query")
def test_update_student_success(mock_execute):
    mock_cursor = type("MockCursor", (), {"rowcount": 1})()
    mock_execute.return_value = mock_cursor

    result = update_student(1, ("x",) * 12)
    assert result == 1


@patch("app.models.student.db.execute_query")
def test_update_student_failure(mock_execute):
    mock_execute.return_value = None
    result = update_student(1, ("x",) * 12)
    assert result == 0


@patch("app.models.student.db.execute_query")
def test_archive_student_success(mock_execute):
    mock_cursor = type("MockCursor", (), {"rowcount": 1})()
    mock_execute.return_value = mock_cursor
    result = archive_student(1)
    assert result == 1


@patch("app.models.student.db.execute_query")
def test_archive_student_failure(mock_execute):
    mock_execute.return_value = None
    result = archive_student(999)
    assert result == 0


# =======================
# Route Tests
# =======================


# ----------- GET /students --------------
@patch("app.routes.student.get_all_active_students")
def test_handle_read_all_active_students_success(
    mock_get, client, valid_student_create_data
):
    mock_get.return_value = valid_student_create_data

    resp = client.get("/students")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Students fetched successfully" in data["message"]
    assert isinstance(data["data"], list)
    assert data["data"] == valid_student_create_data
    mock_get.assert_called_once()


@patch("app.routes.student.get_all_active_students")
def test_handle_read_all_active_students_exception(mock_get_all, client):
    mock_get_all.side_effect = Exception("DB failure")

    response = client.get("/students")
    data = response.get_json()

    assert response.status_code == 500
    assert "Unexpected error: DB failure" in data["error"]
    mock_get_all.assert_called_once()


@patch("app.routes.student.get_student_by_id")
def test_handle_get_student_by_id_success(mock_get_by_id, client):
    mock_get_by_id.return_value = {"id": 1, "first_name": "John"}

    response = client.get("/students/1")
    data = response.get_json()

    assert response.status_code == 200
    assert "Student fetched successfully" in data["message"]
    assert data["data"]["id"] == 1
    mock_get_by_id.assert_called_once_with(1)


@patch("app.routes.student.get_student_by_id")
def test_handle_get_student_by_id_not_found(mock_get_by_id, client):
    mock_get_by_id.return_value = None

    response = client.get("/students/999")
    data = response.get_json()

    assert response.status_code == 404
    assert "Student not found" in data["error"]
    mock_get_by_id.assert_called_once_with(999)


@patch("app.routes.student.get_student_by_id")
def test_handle_get_student_by_id_exception(mock_get_by_id, client):
    mock_get_by_id.side_effect = Exception("DB error")

    response = client.get("/students/1")
    data = response.get_json()

    assert response.status_code == 500
    assert "Unexpected error: DB error" in data["error"]
    mock_get_by_id.assert_called_once_with(1)


@patch("app.routes.student.create_students")
def test_handle_create_student_success(
    mock_create_students, client, valid_student_create_data
):
    mock_create_students.return_value = (valid_student_create_data, None, None)

    response = client.post("/students", json=valid_student_create_data)
    data = response.get_json()

    assert response.status_code == 201
    assert "2 students created successfully" in data["message"]
    assert isinstance(data["data"], dict) or isinstance(data["data"], list)


@patch("app.routes.student.create_students")
def test_handle_create_student_service_error(
    mock_create_students, client, valid_student_create_data
):
    error_data = {"error": "Invalid data"}
    error_code = 422
    mock_create_students.return_value = ([], error_data, error_code)

    response = client.post("/students", json=valid_student_create_data)
    data = response.get_json()

    assert response.status_code == error_code
    assert "Invalid data" in data["error"]


@patch("app.routes.student.create_students")
def test_handle_create_student_key_error(
    mock_create_students, client, valid_student_create_data
):
    mock_create_students.side_effect = KeyError("first_name")

    response = client.post("/students", json=valid_student_create_data)
    data = response.get_json()

    assert response.status_code == 400
    assert "Missing required field" in data["error"]


@patch("app.routes.student.create_students")
def test_handle_create_student_exception(
    mock_create_students, client, valid_student_create_data
):
    mock_create_students.side_effect = Exception("DB failure")

    response = client.post("/students", json=valid_student_create_data)
    data = response.get_json()

    assert response.status_code == 500
    assert "internal error" in data["error"].lower()


@patch("app.routes.student.update_students")
def test_handle_update_students_success(
    mock_update_students, client, valid_student_update_data
):
    mock_update_students.return_value = (valid_student_update_data, None, None)

    response = client.put("/students", json=valid_student_update_data)
    data = response.get_json()

    assert response.status_code == 200
    assert "Student updated successfully" in data["message"]
    assert isinstance(data["data"], dict) or isinstance(data["data"], list)


@patch("app.routes.student.update_students")
def test_handle_update_students_service_error(
    mock_update_students, client, valid_student_update_data
):
    error_data = {"error": "Invalid data"}
    error_code = 422
    mock_update_students.return_value = ([], error_data, error_code)

    response = client.put("/students", json=valid_student_update_data)
    data = response.get_json()

    assert response.status_code == error_code
    assert "Invalid data" in data["error"]


@patch("app.routes.student.update_students")
def test_handle_update_students_key_error(
    mock_update_students, client, valid_student_update_data
):
    mock_update_students.side_effect = KeyError("first_name")

    response = client.put("/students", json=valid_student_update_data)
    data = response.get_json()

    assert response.status_code == 400
    assert "Missing required field" in data["error"]


@patch("app.routes.student.update_students")
def test_handle_update_students_exception(
    mock_update_students, client, valid_student_update_data
):
    mock_update_students.side_effect = Exception("DB failure")

    response = client.put("/students", json=valid_student_update_data)
    data = response.get_json()

    assert response.status_code == 500
    assert "internal error" in data["error"].lower()


# ---------
# PATCH /students - archive students
# ---------


@patch("app.routes.student.archive_students")
def test_handle_archive_students_success(
    mock_archive_students, client, valid_student_ids
):
    mock_archive_students.return_value = valid_student_ids

    response = client.patch("/students", json=valid_student_ids)
    data = response.get_json()

    assert response.status_code == 200
    assert (
        f"{len(valid_student_ids)} student(s) archived successfully" in data["message"]
    )
    assert isinstance(data["data"], list)


@patch("app.routes.student.archive_students")
def test_handle_archive_students_no_students_archived(
    mock_archive_students, client, valid_student_ids
):
    mock_archive_students.return_value = []

    response = client.patch("/students", json=valid_student_ids)
    data = response.get_json()

    assert response.status_code == 404
    assert "No students were archived" in data["error"]


@patch("app.routes.student.archive_students")
def test_handle_archive_students_exception(
    mock_archive_students, client, valid_student_ids
):
    mock_archive_students.side_effect = Exception("DB failure")

    response = client.patch("/students", json=valid_student_ids)
    data = response.get_json()

    assert response.status_code == 500
    assert "internal error" in data["error"].lower()
