## How To

```bash
git clone git@github.com:uncletoxa/maesterd-web.git && cd maesterd_web
```

```bash
touch .flaskenv
```

add to `.flaskenv`:
```markdown
FLASK_APP=app:create_app
SQLALCHEMY_DATABASE_URI=sqlite:///maesterd_web.db
```

```bash
uv venv --python 3.12 && source .venv/bin/activate
```

```bash
cd maesterd_web
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
- [X] fix save_api_key method to save to db  @ momo
- [ ] add go to story button to new story page