from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from salary_api.main import app


DOCS_ROOT = PROJECT_ROOT / "docs"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def swagger_html(spec_url: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Salary Management API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
    <style>
      body {{
        margin: 0;
        background: #f7f4ec;
        color: #1f2937;
        font-family: Georgia, "Times New Roman", serif;
      }}
      .hero {{
        padding: 2rem 2rem 1rem;
        background: linear-gradient(135deg, #f6efe0 0%, #e8f0ef 100%);
        border-bottom: 1px solid #d6d3d1;
      }}
      .hero h1 {{
        margin: 0 0 0.5rem;
        font-size: 2rem;
      }}
      .hero p,
      .hero a {{
        font-size: 1rem;
      }}
      .hero-links {{
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
      }}
      .hero-links a {{
        color: #0f766e;
        text-decoration: none;
        font-weight: 600;
      }}
      #swagger-ui {{
        max-width: 1400px;
        margin: 0 auto;
      }}
    </style>
  </head>
  <body>
    <section class="hero">
      <h1>Salary Management API</h1>
      <p>Public Swagger docs generated from the live FastAPI OpenAPI schema.</p>
      <div class="hero-links">
        <a href="{spec_url}">OpenAPI JSON</a>
      </div>
    </section>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.ui = SwaggerUIBundle({{
        url: "{spec_url}",
        dom_id: "#swagger-ui",
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis],
      }});
    </script>
  </body>
</html>
"""


def main() -> None:
    schema = app.openapi()
    write_text(DOCS_ROOT / "openapi.json", json.dumps(schema, indent=2))
    write_text(DOCS_ROOT / "index.html", swagger_html("./openapi.json"))


if __name__ == "__main__":
    main()
