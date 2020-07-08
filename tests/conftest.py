"""Shared test fixtures.

Pytest will automatically run the setup_teardown_selenium_driver() and
setup_teardown_live_server() functions before a test.  A test function should
use 'live_server' and 'driver' as inputs.

EXAMPLE:
>>> def test_anything(live_server, driver):
>>>     driver.get(live_server.url())
>>>     assert driver.find_elements_by_xpath(".//*")

Pytest fixture docs:
https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions

Google Chrome: a web browser that supports headless browsing.

Selenium: a Python library for controlling a headless web browser.

Chromedriver: middle man executable between Selenium and Chrome.
"""
import os
import time
import logging
import signal
import socket
import urllib
import multiprocessing
import subprocess
from pathlib import Path
import pytest
import flask
import selenium
import selenium.webdriver
import insta485

# Set up logging
LOGGER = logging.getLogger("autograder")

# An implicit wait tells WebDriver to poll the DOM for a certain amount of
# time when trying to find any element (or elements) not immediately
# available. Once set, the implicit wait is set for the life of the
# WebDriver object.
#
# We'll need longer wait times on slow machines like the autograder.
#
# https://selenium-python.readthedocs.io/waits.html#implicit-waits
if "TRAVIS" in os.environ:
    IMPLICIT_WAIT_TIME = 10
elif Path("/home/autograder/working_dir").exists():
    IMPLICIT_WAIT_TIME = 30
else:
    IMPLICIT_WAIT_TIME = 10

# Implicit wait time when using a slow server
IMPLICIT_WAIT_TIME_SLOW_SERVER = 2 * IMPLICIT_WAIT_TIME

# Delay for intentionally slow REST API responses
SLOW_RESPONSE_DELAY = 0.5

# How long to wait for server in separate process to start or stop
SERVER_START_STOP_TIMEOUT = 5


@pytest.fixture(name='app')
def setup_teardown_flask_app():
    """Configure a Flask app object to be used as a live server."""
    LOGGER.info("Setup test fixture 'app'")

    # Sanity check JavaScript distribution bundle.  If it doesn't exist or it's
    # out of date, generate it with webpack.
    bundle_path = Path("insta485/static/js/bundle.js")
    bundle_stale = False
    if bundle_path.exists():
        jsx_mtimes = [
            p.stat().st_mtime for p in Path("insta485/js").glob("*.jsx")
        ]
        bundle_mtime = bundle_path.stat().st_mtime
        bundle_stale = bundle_mtime < max(jsx_mtimes)
    if not bundle_path.exists() or bundle_stale:
        subprocess.run(["npx", "webpack"], check=True)

    # Reset the database
    subprocess.run(["bin/insta485db", "reset"], check=True)

    # Log requests to file. Later, we'll read the log to verify REST API
    # requests made by the client front end show up at the server backend.  We
    # need to log to a file, not an in-memory object because our live server
    # which creates this log will be run in a separate process.
    flask_log_path = Path("flask.log")
    if flask_log_path.exists():
        flask_log_path.unlink()
    werkzeug_logger = logging.getLogger("werkzeug")
    assert not werkzeug_logger.handlers, "Unexpected handler already attached"
    werkzeug_logger.setLevel("INFO")
    werkzeug_logger.addHandler(logging.FileHandler("flask.log"))

    # Configure Flask app.  Testing mode so that exceptions are propagated
    # rather than handled by the the app's error handlers.
    insta485.app.config["TESTING"] = True

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield insta485.app

    # Teardown code starts here
    LOGGER.info("Teardown test fixture 'app'")
    werkzeug_logger.handlers.clear()
    flask_log_path.unlink()


@pytest.fixture(name='live_server')
def setup_teardown_live_server(app):
    """Start app in a separate process."""
    LOGGER.info("Setup test fixture 'live_server'")

    # Start server.  It will automatically find an open port.
    live_server = LiveServer(app)
    live_server.start()

    # Transfer control to testcase
    yield live_server

    # Stop server
    LOGGER.info("Teardown test fixture 'live_server'")
    live_server.stop()


@pytest.fixture(name='driver')
def setup_teardown_selenium_driver():
    """Configure Selenium library to connect to a headless Chrome browser."""
    LOGGER.info("Setup test fixture 'driver'")

    # Configure Selenium
    #
    # Pro-tip: remove the "headless" option and set a breakpoint.  A Chrome
    # browser window will open, and you can play with it using the developer
    # console.
    #
    # We use the "capabilities" object to access the Chrome logs, which is
    # similar to what you'd see in the developer console.   Later, we'll use
    # the logs to check for JavaScript exceptions.
    # Docs: https://stackoverflow.com/questions/44991009/
    options = selenium.webdriver.chrome.options.Options()
    options.add_argument("--headless")  # Don't open a browser GUI window
    options.add_argument("--no-sandbox")  # Required by Docker
    capabilities = selenium.webdriver.common.desired_capabilities.\
        DesiredCapabilities.CHROME
    capabilities['goog:loggingPrefs'] = {'browser': 'SEVERE'}

    driver = selenium.webdriver.Chrome(
        options=options,
        desired_capabilities=capabilities,
    )

    # An implicit wait tells WebDriver to poll the DOM for a certain amount of
    # time when trying to find any element (or elements) not immediately
    # available. Once set, the implicit wait is set for the life of the
    # WebDriver object.
    #
    # https://selenium-python.readthedocs.io/waits.html#implicit-waits
    driver.implicitly_wait(IMPLICIT_WAIT_TIME)
    LOGGER.info("IMPLICIT_WAIT_TIME=%s", IMPLICIT_WAIT_TIME)

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield driver

    # Teardown code starts here
    LOGGER.info("Teardown test fixture 'driver'")

    # Verify no errors in the browser console such as JavaScript exceptions
    # or failed page loads
    console_log = [err["message"] for err in driver.get_log("browser")]
    # Allow errors related to favicon.ico and third-party CSS frameworks
    error_exceptions = ["favicon.ico", "css"]
    console_log_errors = list(
        filter(
            lambda x: all(exp not in x.lower() for exp in error_exceptions),
            console_log,
        )
    )
    assert not console_log_errors,\
        "Errors in browser console:\n{}".format("\n".join(console_log_errors))

    # Clean up the browser processes started by Selenium
    driver.quit()


@pytest.fixture(name='slow_driver')
def setup_teardown_selenium_slow_driver(driver):
    """Replicate 'driver' fixture, but with a longer timeout."""
    LOGGER.info("Setup test fixture 'slow_driver'")

    # Increase the implicit wait time
    driver.implicitly_wait(IMPLICIT_WAIT_TIME_SLOW_SERVER)
    LOGGER.info(
        "IMPLICIT_WAIT_TIME_SLOW_SERVER=%s ",
        IMPLICIT_WAIT_TIME_SLOW_SERVER,
    )

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield driver

    # Teardown code starts here
    LOGGER.info("Teardown test fixture 'slow_driver'")


@pytest.fixture(name='slow_live_server')
def setup_teardown_slow_live_server(app):
    """Start app in a separate process, configured to be artificially slow."""
    LOGGER.info("Setup test fixture 'slow_live_server'")

    # Create a LiveServer object, but don't start it yet
    slow_live_server = LiveServer(app)

    # Function object injects artificial delay
    def delay_request():
        """Delay Flask response to a request."""
        if "/api/v1/" not in flask.request.path:
            return
        LOGGER.info(
            'Delaying response %ss to request "%s %s"',
            SLOW_RESPONSE_DELAY, flask.request.method, flask.request.path,
        )
        time.sleep(SLOW_RESPONSE_DELAY)

    # Register delay as a callback to be executed before each request.  Verify
    # that this function is not already registered.
    for funcs in slow_live_server.app.before_request_funcs.values():
        assert delay_request not in funcs
    app.before_request(delay_request)

    # Start live server *after* registering callback
    slow_live_server.start()

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield slow_live_server

    # Teardown code starts here.  Unregister callback.
    LOGGER.info("Teardown test fixture 'slow_live_server'")
    slow_live_server.stop()
    for funcs in slow_live_server.app.before_request_funcs.values():
        if delay_request in funcs:
            funcs.remove(delay_request)


@pytest.fixture(name="client")
def client_setup_teardown():
    """
    Start a Flask test server with a clean database.

    This fixture is used to test the REST API, it won't start a live server.

    Flask docs: https://flask.palletsprojects.com/en/1.1.x/testing/#testing
    """
    LOGGER.info("Setup test fixture 'client'")

    # Reset the database
    subprocess.run(["bin/insta485db", "reset"], check=True)

    # Configure Flask test server
    insta485.app.config["TESTING"] = True

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    with insta485.app.test_client() as client:
        yield client

    # Teardown code starts here
    LOGGER.info("Teardown test fixture 'client'")


class LiveServer:
    """Represent a Flask app running in a separate process."""

    def __init__(self, app, port=None):
        """Find an open port and create a process object."""
        self.app = app
        self.port = self.get_open_port() if port is None else port
        self.process = multiprocessing.Process(
            target=app.run,
            name="LiveServer",
            kwargs=({
                "port": self.port,
                "use_reloader": False,
                "threaded": True,
            }),
        )

    def url(self):
        """Return base URL of running server."""
        return "http://localhost:{port}/".format(port=self.port)

    def start(self):
        """Start server."""
        self.process.start()
        assert self.wait_for_urlopen()

    def stop(self):
        """Stop server."""
        try:
            os.kill(self.process.pid, signal.SIGINT)
            self.process.join(SERVER_START_STOP_TIMEOUT)
        except multiprocessing.TimeoutError as err:
            LOGGER.error("Failed to join the live server process: %r", err)
        if self.process.is_alive():
            self.process.terminate()

    @staticmethod
    def get_open_port():
        """Return a port that is avaiable for use on localhost."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('', 0))
            port = sock.getsockname()[1]
        return port

    def wait_for_urlopen(self):
        """Call urlopen() in a loop, returning False if it times out."""
        for _ in range(SERVER_START_STOP_TIMEOUT):
            try:
                urllib.request.urlopen(self.url())
                return True
            except urllib.error.URLError:
                time.sleep(1)
        return False
