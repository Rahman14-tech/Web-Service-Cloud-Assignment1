import base64
import re
import sys
import time

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
app = Flask(__name__)

id_map_of_url = {}

# Epoch as a constant start point to calculate the millisecond on the snowflake ID (EPOCH_MS = 1420070400000, is the one that Discord use)
# Source that discord use this Epoch https://en.wikipedia.org/wiki/Snowflake_ID, that we currently used
# Another reference that is used https://bhagwatimalav.substack.com/p/what-is-the-snowflake-unique-id-generator-c45?utm_medium=web (All the links proof that it is being used and scalable)
EPOCH_MS = 1420070400000
WORKER_ID = 0  
SEQ_BITS = 12
WORKER_BITS = 10
MAX_SEQ = (1 << SEQ_BITS) - 1
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def is_url_valid(url):
    """
        Tries to match the given URL for correctness.

        Do so by simply matching it to a regular expression that performs this
        check (see the comment at URL_CORRECTNESS_REGEX).
    """

    # Match with the global regex-expression from the stackoverflow
    return re.match(URL_CORRECTNESS_REGEX, url) is not None

def base62_encode(n: int) -> str:
    if n == 0:
        return ALPHABET[0]
    out = []
    while n > 0:
        n, r = divmod(n, 62)
        out.append(ALPHABET[r])
    return "".join(reversed(out))

class IdGenerator:
    def __init__(self):
        self.last_ms = -1
        self.seq = 0

    def next_int(self) -> int:
        now_ms = int(time.time() * 1000)

        if now_ms == self.last_ms:
            self.seq += 1
            if self.seq > MAX_SEQ:
                # Too many IDs in one ms; wait for next ms
                while now_ms <= self.last_ms:
                    now_ms = int(time.time() * 1000)
                self.seq = 0
        else:
            self.seq = 0
            self.last_ms = now_ms
        t = now_ms - EPOCH_MS
        return (t << (WORKER_BITS + SEQ_BITS)) | (WORKER_ID << SEQ_BITS) | self.seq

    def next_code(self) -> str:
        return base62_encode(self.next_int())

id_generator = IdGenerator()

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
        # Generate new identifier for the URL
        url_identifier = id_generator.next_code()
        # Insert the ID with the url in map
        id_map_of_url[url_identifier] = url

        # Return the url identifier and the status code 201 meaning success
        return url_identifier,201
        
    elif request.method == "DELETE":
     if not id_map_of_url:
        return "No URLs to delete", 404
     else:
        id_map_of_url.clear()
        return "All URLs deleted", 200

@app.route("/<string:id>",methods = ['GET','PUT','DELETE'])
def url_with_id(id):
    if request.method == "GET":
        if id in id_map_of_url:
            # Redirect user to the related id in the map
            # The redirect() function will automatically set the correct headers and status code
            return redirect(id_map_of_url[id])
        else:
            # Url of that Id is not found
            abort(404)
    elif request.method == "PUT":
        pass
    elif request.method == "DELETE":
        pass
    pass