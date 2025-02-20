```bash
touch .flaskenv
```

add to `.flaskenv`

```markdown
FLASK_APP=app:create_app
SQLALCHEMY_DATABASE_URI=sqlite:///maesterd_web.db
```

```bash
uv run flask db init
uv run flask db migrate
uv run flask db upgrade
```

```bash
uv run flask run --debug
```
