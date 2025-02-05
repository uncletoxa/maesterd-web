```commandline
export FLASK_APP=maesterd_web
export SQLALCHEMY_DATABASE_URI="sqlite:///maesterd_web.db"
```

```commandline
flask db init
flask db migrate
flask db upgrade
```

```commandline
flask run --debug
```
