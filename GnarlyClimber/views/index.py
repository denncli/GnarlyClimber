"""
GnarlyClimber search (main) view.

URLs include:
/
"""
import flask
import GnarlyClimber


@GnarlyClimber.app.route('/')
def show_index():
    """Display / route."""
    context = {}
    return flask.render_template("index.html", **context)
