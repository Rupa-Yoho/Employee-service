import json

import pytest
from fastapi.testclient import TestClient

from src import main

SAMPLE = [
    {"name": "Arun", "department": "Sales", "salary": 30000},
    {"name": "Divya", "department": "IT", "salary": 75000},
]


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Each test uses its own temporary employees.json."""
    data_file = tmp_path / "employees.json"
    data_file.write_text(json.dumps(SAMPLE), encoding="utf-8")
    monkeypatch.setattr(main, "DATA_FILE", data_file)
    return TestClient(main.app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_employees(client):
    response = client.get("/employees")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_employee_success(client):
    response = client.get("/employees/Divya")
    assert response.status_code == 200
    assert response.json()["salary"] == 75000


def test_get_employee_not_found(client):
    response = client.get("/employees/Ravi")
    assert response.status_code == 404


def test_create_employee_success(client):
    payload = {"name": "Meena", "department": "HR", "salary": 40000}
    response = client.post("/employees", json=payload)
    assert response.status_code == 201
    assert len(client.get("/employees").json()) == 3


def test_create_employee_invalid_salary(client):
    payload = {"name": "Meena", "department": "HR", "salary": -5}
    response = client.post("/employees", json=payload)
    assert response.status_code == 422


def test_create_employee_empty_name(client):
    payload = {"name": "  ", "department": "HR", "salary": 40000}
    response = client.post("/employees", json=payload)
    assert response.status_code == 422
