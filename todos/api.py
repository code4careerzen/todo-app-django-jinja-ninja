# todos/api.py
from typing import List
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from .auth import HARDCODED_PASSWORD, HARDCODED_USERNAME, combined_auth, create_jwt_token
from .models import Todo

api = NinjaAPI(title="Todo API")


# --- Schemas ---
class LoginIn(Schema):
    username: str
    password: str


class TokenOut(Schema):
    access_token: str
    token_type: str = "bearer"


class TodoIn(Schema):
    title: str


class TodoOut(Schema):
    id: int
    title: str
    completed: bool


# --- Auth Route ---
@api.post("/login", response=TokenOut)
def login_for_token(request, data: LoginIn):
    if data.username != HARDCODED_USERNAME or data.password != HARDCODED_PASSWORD:
        raise HttpError(401, "Invalid username or hardcoded password")

    # Also log into Django session so django_auth works seamlessly if needed
    user, _ = User.objects.get_or_create(username=HARDCODED_USERNAME)
    login(request, user)

    token = create_jwt_token(data.username)
    return {"access_token": token}


# --- Protected Todo Routes ---
@api.get("/todos", response=List[TodoOut], auth=combined_auth)
def list_todos(request):
    return Todo.objects.order_by("-created_at")


@api.post("/todos", response=TodoOut, auth=combined_auth)
def create_todo(request, data: TodoIn):
    return Todo.objects.create(title=data.title)


@api.patch("/todos/{todo_id}/toggle", response=TodoOut, auth=combined_auth)
def toggle_todo(request, todo_id: int):
    todo = get_object_or_404(Todo, id=todo_id)
    todo.completed = not todo.completed
    todo.save()
    return todo


@api.delete("/todos/{todo_id}", auth=combined_auth)
def delete_todo(request, todo_id: int):
    todo = get_object_or_404(Todo, id=todo_id)
    todo.delete()
    return {"success": True}
