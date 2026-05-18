# -----------------------------------------------------------------------------
#  EnvComparer Controller - Crafted with ♥ by codesaksham
#  A premium developer utility to align, parse, and compare environment lists.
#  Copyright (c) 2026 codesaksham. All rights reserved.
# -----------------------------------------------------------------------------

import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.parser import EnvParser, EnvComparer

app = FastAPI(
    title="EnvComparer",
    description="A premium developer utility to compare and align environment variables.",
    version="1.0.0",
)

# Set up templates directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Sample data for initial engagement
SAMPLE_LEFT = """# Database Settings
DATABASE_URL="postgresql://postgres:secret@localhost:5432/production"
DB_TIMEOUT=30
MAX_CONNECTIONS=100

# Auth & Security
JWT_SECRET="prod-super-secret-key-12345"
SESSION_LIFETIME=3600
OIDC_ENABLED=true

# Server Config
PORT=8000
PORT=9000
DEBUG=false
ALLOWED_HOSTS="app.company.com,api.company.com"

# Storage
MINIO_ENDPOINT="s3.amazonaws.com"
MINIO_ACCESS_KEY="AKIAIOSFODNN7EXAMPLE"
MINIO_SECRET_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
"""

SAMPLE_RIGHT = """# Database Settings
DATABASE_URL="postgresql://postgres:devpassword@localhost:5432/development"
DB_TIMEOUT=60
DB_TIMEOUT=90
MAX_CONNECTIONS=20

# Auth & Security
JWT_SECRET="dev-insecure-key-only"
SESSION_LIFETIME=86400
# OIDC_ENABLED is commented out in dev
# OIDC_ENABLED=false

# Server Config
PORT=8080
DEBUG=true
ALLOWED_HOSTS="*"

# Extra Dev Config
DEV_AUTO_LOGIN=true
MOCK_EMAIL_SERVICE=true
"""


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Renders the main index page with empty fields or placeholders."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "left_content": "",
            "right_content": "",
            "sample_left": SAMPLE_LEFT,
            "sample_right": SAMPLE_RIGHT,
            "has_results": False,
            "diff_items": [],
            "stats": {},
            "left_label": "Environment List A",
            "right_label": "Environment List B",
            "safe_keys_str": "",
        },
    )


@app.post("/", response_class=HTMLResponse)
async def compare_envs(
    request: Request,
    left_content: str = Form(""),
    right_content: str = Form(""),
    left_label: str = Form("Environment List A"),
    right_label: str = Form("Environment List B"),
    safe_keys: str = Form(""),
):
    """
    Handles form submission POST requests.
    Parses both inputs, custom labels, and safe keys, performs key alignment comparison, and returns the template with results.
    """
    # Parse safe keys set
    safe_keys_set = {k.strip() for k in safe_keys.split(",") if k.strip()}

    left_dict, left_dups = EnvParser.parse(left_content)
    right_dict, right_dups = EnvParser.parse(right_content)

    diff_items, stats = EnvComparer.compare(
        left_dict=left_dict,
        right_dict=right_dict,
        left_duplicates=left_dups,
        right_duplicates=right_dups,
        safe_keys=safe_keys_set,
    )

    # Convert diff_items to lists of dicts for seamless JSON/Jinja interaction if needed
    diff_items_dicts = [item.to_dict() for item in diff_items]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "left_content": left_content,
            "right_content": right_content,
            "sample_left": SAMPLE_LEFT,
            "sample_right": SAMPLE_RIGHT,
            "has_results": True,
            "diff_items": diff_items_dicts,
            "stats": stats,
            "left_label": left_label,
            "right_label": right_label,
            "safe_keys_str": safe_keys,
        },
    )


@app.post("/api/compare")
async def api_compare(request: Request):
    """
    REST API endpoint for dynamic JSON-based comparisons.
    """
    data = await request.json()
    left_content = data.get("left_content", "")
    right_content = data.get("right_content", "")
    left_label = data.get("left_label", "Environment List A")
    right_label = data.get("right_label", "Environment List B")
    safe_keys = data.get("safe_keys", "")

    # Parse safe keys set
    if isinstance(safe_keys, list):
        safe_keys_set = set(safe_keys)
        safe_keys_str = ",".join(safe_keys)
    else:
        safe_keys_set = {k.strip() for k in safe_keys.split(",") if k.strip()}
        safe_keys_str = safe_keys

    left_dict, left_dups = EnvParser.parse(left_content)
    right_dict, right_dups = EnvParser.parse(right_content)

    diff_items, stats = EnvComparer.compare(
        left_dict=left_dict,
        right_dict=right_dict,
        left_duplicates=left_dups,
        right_duplicates=right_dups,
        safe_keys=safe_keys_set,
    )
    diff_items_dicts = [item.to_dict() for item in diff_items]

    return {
        "success": True,
        "diff_items": diff_items_dicts,
        "stats": stats,
        "left_label": left_label,
        "right_label": right_label,
        "safe_keys_str": safe_keys_str,
    }
