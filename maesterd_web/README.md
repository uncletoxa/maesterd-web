```bash
export FLASK_APP=maesterd_web
export SQLALCHEMY_DATABASE_URI="sqlite:///maesterd_web.db"
```

```bash
flask db init
flask db migrate
flask db upgrade
```

```bash
flask run --debug
```
