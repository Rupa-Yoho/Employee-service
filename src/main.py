import json
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "employees.json"
app = FastAPI(title="Employee Data Service")


class Employee(BaseModel):
    name: str
    department: str
    salary: float = Field(gt=0)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name must not be empty")
        return value.strip()


def load_employees() -> List[dict]:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_employees(employees: List[dict]) -> None:
    DATA_FILE.write_text(json.dumps(employees, indent=2), encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/employees")
def list_employees() -> List[dict]:
    return load_employees()


@app.get("/employees/{name}")
def get_employee(name: str) -> dict:
    employees = load_employees()
    for emp in employees:
        if emp["name"].strip().lower() == name.strip().lower():
            return emp
    raise HTTPException(status_code=404, detail="Employee not found")


@app.post("/employees", status_code=201)
def create_employee(employee: Employee) -> dict:
    employees = load_employees()
    new = employee.model_dump()
    employees.append(new)
    save_employees(employees)
    return new
