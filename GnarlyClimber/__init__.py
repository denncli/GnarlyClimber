"""Insta485 package initializer."""
import flask

# app is a single object used by all the code modules in this package
app = flask.Flask(__name__)  # pylint: disable=invalid-name

# Read settings from config module (GnarlyClimber/config.py)
app.config.from_object('GnarlyClimber.config')

# Overlay settings read from file specified by environment variable. This is
# useful for using different on development and production machines.
# Reference: http://flask.pocoo.org/docs/config/
app.config.from_envvar('GNARLYCLIMBER_SETTINGS', silent=True)

# Tell our app about views and model.  This is dangerously close to a
# circular import, which is naughty, but Flask was designed that way.
# (Reference http://flask.pocoo.org/docs/patterns/packages/)  We're
# going to tell pylint and pycodestyle to ignore this coding style violation.
import GnarlyClimber.views  # noqa: E402  pylint: disable=wrong-import-position
import GnarlyClimber.model  # noqa: E402  pylint: disable=wrong-import-position
import GnarlyClimber.api  # noqa: E402  pylint: disable=wrong-import-position