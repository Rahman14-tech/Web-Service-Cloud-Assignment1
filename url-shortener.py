import base64
import re
import sys

from flask import Flask, abort, redirect, request


# ### CONSTANTS ###
# Regular expressions that is used to check URLs for correctness.
# Taken from: https://stackoverflow.com/a/7995979
URL_CORRECTNESS_REGEX = (
    r"(?i)"                                                             # We activate the case-insensitivity extension for this regex. See the Python docs for more info: https://docs.python.org/3/library/re.html#regular-expression-syntax (see `(?...)`)
    r"^https?://"                                                       # Matches the start of the string (`^`) and then the `http://` or `https://` scheme
    r"(?:"                                                              # Matches either:
        r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?"         # A domain name, which consists of various subdomains separated by dots. Each of those matches an alphanumeric character, optionally followed by either 0-61 alphanumeric characters or dashes and another single alhpanumeric character. Finally, there is a letter-only toplevel domain name of 2-6 characters and an optional dot.
        r"|"                                                            # OR
        r"localhost"                                                        # We match 'localhost' literally
        r"|"                                                            # OR
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"                               # We match an IPv4 address, which are four sets of 1-3 digits.
    r")"
    r"(?::\d+)?"                                                        # Then we match an optional port, consisting of at least one digit. Note that the double colon is actually part of `(?:)`, which means a matched but not saved string.
    r"(?:/?|[/?]\S+)$"                                                  # Finally, we match an optional slash or a (slash or question mark) followed by at least one non-whitespace character. This effectively makes most of the paths wildcards, as they can be anything; but because paths can container arbitrary information, this is OK. At last we match the end-of-string boundary, `$`.
)

def is_url_valid(url):
    """
        Tries to match the given URL for correctness.

        Do so by simply matching it to a regular expression that performs this
        check (see the comment at URL_CORRECTNESS_REGEX).
    """

    # Match with the global regex-expression from the stackoverflow
    return re.match(URL_CORRECTNESS_REGEX, url) is not None

app = Flask(__name__)

id_map_of_url = {}
worker_id = 0
seq_bits = 12

def id_generator():
    pass

@app.route("/", methods=['GET', 'POST', 'DELETE'])
def root():
    if request.method == "GET":
        return { "ids:urls": id_map_of_url }
    elif request.method == "POST":
        if "url" not in request.form:
            return "URL is not present",400
        url = request.form["url"]
        if not is_url_valid(url):
            return "URL is not valid"
        pass
    elif request.method == "DELETE":
        pass

@app.route("/<string:id>",methods = ['GET','PUT','DELETE'])
def url_with_id(id):
    if request.method == "GET":
        pass
    elif request.method == "PUT":
        pass
    elif request.method == "DELETE":
        pass
    pass