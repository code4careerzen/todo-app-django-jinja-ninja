from django.shortcuts import render
from .auth import HARDCODED_PASSWORD, HARDCODED_USERNAME

def index(request):
    return render(
        request,
        "todos/index.jinja",
        {
            "default_user": HARDCODED_USERNAME,
            "default_pass": HARDCODED_PASSWORD,
        },
    )
