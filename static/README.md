# Static Assets

This folder contains static files served by the Flask server.

## Useful Links
- `/static/test.html` — sample static page
- `/static/links.html` — simple list of links
- `/generate_doc` — generate a sample PDF document from conversation

## Configuration
- Static directory is controlled by `STATIC_DIR` environment variable.
- Defaults to `static` at the project root.

## Example
- Start server: `./spoon-env/bin/python server.py`
- Open: `http://127.0.0.1:8000/static/test.html`