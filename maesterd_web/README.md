## How To

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

## To Dos


- [ ] turn the project into uv (all)
- [x] expose char creation to new story page  @momo
- [x] expose setting to new story page  @momo
- [x] create custom char creation input @momo
- [ ] add go to story button to new story page