"""P3 utility functions."""
import re
import time
import pathlib
import logging
import conftest


# Temporary directory.  Tests will create files here.
TMPDIR = pathlib.Path("tmp")

# Directory containing unit tests.  Tests look here for input files.
TEST_DIR = pathlib.Path(__file__).parent

# Set up logging
LOGGER = logging.getLogger("autograder")


def assert_no_browser_console_errors(driver):
    """Raise AssertionError if any messages are present in the browser console.

    In the 'driver' fixture implemented in conftest.py, we set the browser
    console logging level to severe.  This function verifies that the list of
    console message is empty.
    """
    console_log = driver.get_log("browser")
    console_log_empty = not console_log
    console_log_str = "\n".join(x["message"] for x in console_log)
    assert console_log_empty,\
        "Error in browser console:\n{}".format(console_log_str)


def wait_for_api_calls(path, n_calls, timeout=conftest.IMPLICIT_WAIT_TIME):
    """Return when 'path' contains >='calls' lines or timeout occurs."""
    flask_log = ""
    pattern = re.compile(r"/api/.*$")  # Regex that matches API calls
    for _ in range(2 * timeout):
        with open(path) as infile:
            flask_log = infile.read()
        cur_calls = len(pattern.findall(flask_log))
        if cur_calls >= n_calls:
            break
        LOGGER.info("Waiting for %s lines in '%s'", n_calls, path)
        time.sleep(0.5)
    return flask_log


def scroll_to_bottom_of_page(driver):
    """Scroll to bottom of the page by finding the tallest DOM element."""
    get_largest_height_script = """
        let elements = document.getElementsByTagName("*");
        let current_max = 0;
        for (let i = 0; i < elements.length; i++) {
            if (elements[i].scrollHeight > current_max) {
                current_max = elements[i].scrollHeight;
            }
        }
        return current_max;
    """
    largest_height = driver.execute_script(get_largest_height_script)

    scroll_script = "window.scrollTo(0, {});".format(largest_height)
    driver.execute_script(scroll_script)
    assert_no_browser_console_errors(driver)
