import pytest
from datetime import date
from unittest.mock import patch
from app.models import (
    student_db_read_all,
    student_db_read_by_id,
    student_db_read_by_ids,
    student_db_insert,
    student_db_update,
    student_db_archive,
)
from app.services import (
    get_all_students,
    get_student_by_id,
    create_new_students,
    update_students,
    archive_students,
)

# =======================
# Fixtures
# =======================


def make_student_row():
    today = date.today().isoformat()
    return (
        1,
        "John",
        "Doe",
        "johndoe@example.com",
        "123 Main St",
        "Anytown",
        "ON",
        "Canada",
        "local",
        "active",
        0,
        0,
        1,
        today,
        today,
        0,
    )


def make_student_dict():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "is_international": False,
    }


@pytest.fixture
def valid_student_row():
    return make_student_row()


@pytest.fixture
def valid_student_rows():
    return [make_student_row() for _ in range(2)]


@pytest.fixture
def valid_student_create_data():
    return [
        make_student_dict(),
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "janedoe@example.com",
            "is_international": True,
        },
    ]


@pytest.fixture
def valid_student_update_data():
    data = make_student_dict()
    data["id"] = 1
    return [data]


@pytest.fixture
def student_missing_id(valid_student_update_data):
    data = [item.copy() for item in valid_student_update_data]
    for d in data:
        d.pop("id", None)
    return data


@pytest.fixture
def valid_student_ids():
    return [1, 2]


# =======================
# DB Mock Fixtures
# =======================


@pytest.fixture
def mock_db_read_all():
    with patch("app.services.student.student_db_read_all") as mock:
        yield mock


@pytest.fixture
def mock_db_read_one():
    with patch("app.services.student.student_db_read_by_id") as mock:
        yield mock


@pytest.fixture
def mock_db_read_many():
    with patch("app.services.student.student_db_read_by_ids") as mock:
        yield mock


@pytest.fixture
def mock_db_create():
    with patch("app.services.student.student_db_insert") as mock:
        yield mock


@pytest.fixture
def mock_db_update():
    with patch("app.services.student.student_db_update") as mock:
        yield mock


@pytest.fixture
def mock_db_archive():
    with patch("app.services.student.student_db_archive") as mock:
        yield mock


# =======================
# Service Tests
# =======================


class TestStudentReadService:
    def test_get_all_students(self, mock_db_read_all, valid_student_row):
        mock_db_read_all.return_value = [valid_student_row]
        students = get_all_students(active_only=True)
        assert len(students) == 1
        assert students[0]["first_name"] == "John"
        mock_db_read_all.assert_called_once()

    def test_get_all_students_none(self, mock_db_read_all):
        mock_db_read_all.return_value = None
        with pytest.raises(RuntimeError):
            get_all_students(active_only=True)

    def test_get_student_by_id(self, mock_db_read_one, valid_student_row):
        mock_db_read_one.return_value = valid_student_row
        student = get_student_by_id(1)
        assert student["first_name"] == "John"
        mock_db_read_one.assert_called_once_with(1)

    def test_get_student_by_id_not_found(self, mock_db_read_one):
        mock_db_read_one.return_value = None
        student = get_student_by_id(123)
        assert student is None


class TestStudentCreateService:
    def test_create_new_students(
        self,
        mock_db_create,
        mock_db_read_many,
        valid_student_create_data,
        valid_student_rows,
    ):
        mock_db_create.side_effect = [1, 2]
        mock_db_read_many.return_value = valid_student_rows

        results, error, status_code = create_new_students(valid_student_create_data)

        assert len(results) == 2
        assert error is None
        assert status_code == 201
        assert mock_db_create.call_count == 2
        mock_db_read_many.assert_called_once_with([1, 2])

    def test_create_new_students_failure(
        self, mock_db_create, mock_db_read_many, valid_student_create_data
    ):
        mock_db_create.side_effect = [None, None]
        results, error, status_code = create_new_students(valid_student_create_data)

        assert results == []
        assert error["message"] == "No students were created"
        assert status_code == 400
        mock_db_read_many.assert_not_called()


class TestStudentUpdateService:
    def test_update_students(
        self,
        mock_db_update,
        mock_db_read_many,
        valid_student_update_data,
        valid_student_row,
    ):
        mock_db_update.return_value = 1
        mock_db_read_many.return_value = [valid_student_row]

        results, error, status_code = update_students(valid_student_update_data)

        assert len(results) == 1
        assert error == []
        assert status_code == 200
        assert mock_db_update.call_count == 1
        mock_db_read_many.assert_called_once_with([1])

    def test_update_students_no_success(
        self, mock_db_update, mock_db_read_many, valid_student_update_data
    ):
        mock_db_update.return_value = 0
        results, error, status_code = update_students(valid_student_update_data)

        assert results == []
        assert error == [{"message": "Student ID 1 not updated."}]
        assert status_code == 400
        mock_db_update.assert_called_once()
        mock_db_read_many.assert_not_called()

    def test_update_students_missing_id(
        self, mock_db_update, mock_db_read_many, student_missing_id
    ):
        results, error, status_code = update_students(student_missing_id)

        assert results == []
        assert error == [{"message": "Missing student ID for update."}]
        assert status_code == 400
        mock_db_update.assert_not_called()
        mock_db_read_many.assert_not_called()


class TestStudentArchiveService:
    def test_archive_students(self, mock_db_archive, valid_student_ids):
        mock_db_archive.side_effect = [1, 1]
        archived = archive_students(valid_student_ids)

        assert len(archived[0]) == 2
        assert mock_db_archive.call_count == 2

    def test_archive_students_none_archived(self, mock_db_archive, valid_student_ids):
        mock_db_archive.return_value = 0
        archived = archive_students(valid_student_ids)

        assert archived[0] == []

    def test_archive_students_invalid_ids(self):
        results, errors, status = archive_students(["one", 2])
        assert status == 400
        assert any("must be integers" in e["message"] for e in errors)


# =======================
# Model Tests
# =======================


class TestStudentModel:
    @patch("app.models.student.db.execute_query")
    def test_student_db_read_all(self, mock_execute):
        mock_execute.return_value = [("mocked",)]
        result = student_db_read_all()
        assert result == [("mocked",)]
        mock_execute.assert_called_once_with("SELECT * FROM students;")

    @patch("app.models.student.db.execute_query")
    def test_student_db_read_all_active(self, mock_execute):
        mock_execute.return_value = [("active_student",)]
        result = student_db_read_all(active_only=True)
        assert result == [("active_student",)]
        mock_execute.assert_called_once_with(
            "SELECT * FROM students WHERE status = 'active';"
        )

    @patch("app.models.student.db.execute_query")
    def test_student_db_read_by_id_found(self, mock_execute):
        mock_execute.return_value = [("student_1",)]
        result = student_db_read_by_id(1)
        assert result == ("student_1",)
        mock_execute.assert_called_once_with(
            "SELECT * FROM students WHERE id = ?;", (1,)
        )

    @patch("app.models.student.db.execute_query")
    def test_student_db_read_by_id_not_found(self, mock_execute):
        mock_execute.return_value = []
        result = student_db_read_by_id(999)
        assert result is None
        mock_execute.assert_called_once()

    @patch("app.models.student.db.execute_query")
    def test_student_db_read_by_ids_empty_list(self, mock_execute):
        result = student_db_read_by_ids([])
        assert result == []
        mock_execute.assert_not_called()

    @patch("app.models.student.db.execute_query")
    def test_student_db_read_by_ids_success(self, mock_execute):
        mock_execute.return_value = [("s1",), ("s2",)]
        result = student_db_read_by_ids([1, 2])

        assert result == [("s1",), ("s2",)]
        mock_execute.assert_called_once()
        assert "IN (?,?)" in mock_execute.call_args.args[0]
        assert mock_execute.call_args.args[1] == [1, 2]

    @patch("app.models.student.db.execute_query")
    def test_student_db_insert_success(self, mock_execute, valid_student_row):
        mock_cursor = type("MockCursor", (), {"lastrowid": 10})()
        mock_execute.return_value = mock_cursor

        params = valid_student_row
        result = student_db_insert(params)

        assert result == 10
        mock_execute.assert_called_once()

        query, called_params = mock_execute.call_args.args
        assert "INSERT INTO students" in query
        assert called_params == params

    @patch("app.models.student.db.execute_query")
    def test_student_db_insert_failure(self, mock_execute):
        mock_execute.return_value = None
        result = student_db_insert(("bad",))
        assert result is None

    @patch("app.models.student.db.execute_query")
    def test_student_db_update_success(self, mock_execute):
        mock_cursor = type("MockCursor", (), {"rowcount": 1})()
        mock_execute.return_value = mock_cursor

        result = student_db_update(1, ("x",) * 12)
        assert result == 1

    @patch("app.models.student.db.execute_query")
    def test_student_db_update_failure(self, mock_execute):
        mock_execute.return_value = None
        result = student_db_update(1, ("x",) * 12)
        assert result == 0

    @patch("app.models.student.db.execute_query")
    def test_student_db_archive_success(self, mock_execute):
        mock_cursor = type("MockCursor", (), {"rowcount": 1})()
        mock_execute.return_value = mock_cursor
        result = student_db_archive(1)
        assert result == 1

    @patch("app.models.student.db.execute_query")
    def test_student_db_archive_failure(self, mock_execute):
        mock_execute.return_value = None
        result = student_db_archive(999)
        assert result == 0


# =======================
# Route Tests
# =======================


class TestStudentReadRoute:
    @patch("app.routes.student.get_all_students")
    def test_handle_student_db_read_all_success(
        self, mock_get, client, valid_student_create_data
    ):
        mock_get.return_value = valid_student_create_data

        resp = client.get("/students")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "Students fetched successfully." in data["message"]
        assert isinstance(data["data"], list)
        assert data["data"] == valid_student_create_data
        mock_get.assert_called_once()

    @patch("app.routes.student.get_all_students")
    def test_handle_student_db_read_all_exception(self, mock_get_all, client):
        mock_get_all.side_effect = Exception("DB failure")

        response = client.get("/students")
        data = response.get_json()

        assert response.status_code == 500
        assert "Unexpected error: DB failure" in data["error"]
        mock_get_all.assert_called_once()

    @patch("app.routes.student.get_student_by_id")
    def test_handle_get_student_by_id_success(self, mock_get_by_id, client):
        mock_get_by_id.return_value = {"id": 1, "first_name": "John"}

        response = client.get("/students/1")
        data = response.get_json()

        assert response.status_code == 200
        assert "Student fetched successfully" in data["message"]
        assert data["data"]["id"] == 1
        mock_get_by_id.assert_called_once_with(1)

    @patch("app.routes.student.get_student_by_id")
    def test_handle_get_student_by_id_not_found(self, mock_get_by_id, client):
        mock_get_by_id.return_value = None

        response = client.get("/students/999")
        data = response.get_json()

        assert response.status_code == 404
        assert "Student not found" in data["error"]
        mock_get_by_id.assert_called_once_with(999)

    @patch("app.routes.student.get_student_by_id")
    def test_handle_get_student_by_id_exception(self, mock_get_by_id, client):
        mock_get_by_id.side_effect = Exception("DB error")

        response = client.get("/students/1")
        data = response.get_json()

        assert response.status_code == 500
        assert "Unexpected error: DB error" in data["error"]
        mock_get_by_id.assert_called_once_with(1)


class TestStudentCreateRoute:
    @patch("app.routes.student.create_new_students")
    def test_handle_student_db_insert_success(
        self, mock_create_new_students, client, valid_student_create_data
    ):
        mock_create_new_students.return_value = (valid_student_create_data, None, None)

        response = client.post("/students", json=valid_student_create_data)
        data = response.get_json()

        assert response.status_code == 201
        assert "2 students created successfully" in data["message"]
        assert data["data"]

    @patch("app.routes.student.create_new_students")
    def test_handle_student_db_insert_service_error(
        self, mock_create_new_students, client, valid_student_create_data
    ):
        error_data = {"message": "Invalid data"}
        error_code = 400
        mock_create_new_students.return_value = ([], error_data, error_code)

        response = client.post("/students", json=valid_student_create_data)
        data = response.get_json()

        assert response.status_code == error_code
        assert "Invalid data" in data["message"]

    @patch("app.routes.student.create_new_students")
    def test_handle_student_db_insert_key_error(
        self, mock_create_new_students, client, valid_student_create_data
    ):
        mock_create_new_students.side_effect = KeyError("first_name")

        response = client.post("/students", json=valid_student_create_data)
        data = response.get_json()

        assert response.status_code == 400
        assert "Missing required field" in data["error"]

    @patch("app.routes.student.create_new_students")
    def test_handle_student_db_insert_exception(
        self, mock_create_new_students, client, valid_student_create_data
    ):
        mock_create_new_students.side_effect = Exception("DB failure")

        response = client.post("/students", json=valid_student_create_data)
        data = response.get_json()

        assert response.status_code == 500
        assert "internal error" in data["error"].lower()


class TestStudentUpdateRoute:
    @patch("app.routes.student.update_students")
    def test_handle_update_students_success(
        self, mock_update_students, client, valid_student_update_data
    ):
        mock_update_students.return_value = (valid_student_update_data, None, None)

        response = client.put("/students", json=valid_student_update_data)
        data = response.get_json()

        assert response.status_code == 200
        assert "Student updated successfully" in data["message"]
        assert data["data"]

    @patch("app.routes.student.update_students")
    def test_handle_update_students_service_error(
        self, mock_update_students, client, valid_student_update_data
    ):
        error_data = {"message": "Invalid data"}
        error_code = 422
        mock_update_students.return_value = ([], error_data, error_code)

        response = client.put("/students", json=valid_student_update_data)
        data = response.get_json()

        assert response.status_code == error_code
        assert "Invalid data" in data["message"]

    @patch("app.routes.student.update_students")
    def test_handle_update_students_key_error(
        self, mock_update_students, client, valid_student_update_data
    ):
        mock_update_students.side_effect = KeyError("first_name")

        response = client.put("/students", json=valid_student_update_data)
        data = response.get_json()

        assert response.status_code == 400
        assert "Missing required field" in data["error"]

    @patch("app.routes.student.update_students")
    def test_handle_update_students_exception(
        self, mock_update_students, client, valid_student_update_data
    ):
        mock_update_students.side_effect = Exception("DB failure")

        response = client.put("/students", json=valid_student_update_data)
        data = response.get_json()

        assert response.status_code == 500
        assert "internal error" in data["error"].lower()


class TestStudentArchiveRoute:
    @patch("app.routes.student.archive_students")
    def test_handle_archive_students_success(
        self, mock_archive_students, client, valid_student_ids
    ):
        mock_archive_students.return_value = (valid_student_ids, None, 200)

        response = client.patch("/students", json={"ids": valid_student_ids})
        data = response.get_json()

        assert response.status_code == 200
        assert "2 students archived successfully" in data["message"]
        assert data["data"]

    @patch("app.routes.student.archive_students")
    def test_handle_archive_students_service_error(
        self, mock_archive_students, client, valid_student_ids
    ):
        error_data = {"message": "No students were archived."}
        error_code = 400
        mock_archive_students.return_value = ([], error_data, error_code)

        response = client.patch("/students", json={"ids": valid_student_ids})
        data = response.get_json()

        assert response.status_code == error_code
        assert "No students were archived." in data["message"]

    @patch("app.routes.student.archive_students")
    def test_handle_archive_students_key_error(
        self, mock_archive_students, client, valid_student_ids
    ):
        mock_archive_students.side_effect = KeyError("ids")

        response = client.patch("/students", json={"ids": valid_student_ids})
        data = response.get_json()

        assert response.status_code == 400
        assert "Missing required field" in data["error"]

    @patch("app.routes.student.archive_students")
    def test_handle_archive_students_exception(
        self, mock_archive_students, client, valid_student_ids
    ):
        mock_archive_students.side_effect = Exception("DB failure")

        response = client.patch("/students", json={"ids": valid_student_ids})
        data = response.get_json()

        assert response.status_code == 500
        assert "internal error" in data["error"].lower()
