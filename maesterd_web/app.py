from flask import Flask, render_template

def register_blueprints(app):
    """Register Flask blueprints."""
    # app.register_blueprint(public.views.blueprint)
    # app.register_blueprint(user.views.blueprint)
    return None


def register_error_handlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"errors/{error_code}.html"), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None
