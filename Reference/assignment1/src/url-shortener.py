#!/bin/env python3

# URL SHORTENER.py
#   by Tim Müller
#
# Created:
#   03 Mar 2022, 14:25:23
# Last edited:
#   02 May 2023, 11:44:54
# Auto updated?
#   Yes
#
# Description:
#   Implements a simple URL-shortening RESTful service.
#   Built with the Flask (https://flask.palletsprojects.com/en/2.0.x/)
#   framework.
#
#   In this service, we try to assign a short identifier to each new URL. This
#   is implemented by using a static counter for the ID, and then encoding the
#   number as Base64. This way, we use base64 as a more efficient number
#   encoding scheme than ASCII.
#

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





### GLOBAL VALUES ###
# Keeps track of the next numeric identifier
next_id = 0

# In-memory database of the URLs we have shortened
id_url_map = {}





### HELPER FUNCTIONS ###
def generate_id():
    """
        Generates a new identifier.

        Does so by serializing the global `next_id` to Base64 instead of ASCII
        for better compression.
    """

    # Don't forget to mark next_id as global, as otherwise updating it won't update the global
    # variable
    global next_id

    # Get the ID and increment it
    identifier = next_id
    next_id += 1

    # We find the number of bytes we would need to represent the number.
    # We do this because Python's numbers are not really stored most efficiently per sé, so we take the minimum number of bytes
    n_bytes = 1 + identifier.bit_length() // 8

    # Serialize the number; we get it as an array of bytes (endianness does not matter, as long as
    # it's the same across all IDs, and then encode that byte string as Base64)
    sidentifier = base64.urlsafe_b64encode(identifier.to_bytes(n_bytes, sys.byteorder)).decode("utf-8")

    # We can strip the padding (`=`) from the identifier, since this is superfluous information (is purely reconstructable from the length of the string, if needed)
    while sidentifier[-1] == '=': sidentifier = sidentifier[:-1]

    # Done
    next_id += 1
    return sidentifier

def valid_url(url):
    """
        Tries to match the given URL for correctness.

        Do so by simply matching it to a regular expression that performs this
        check (see the comment at URL_CORRECTNESS_REGEX).
    """

    # Match with the global regex-expression
    return re.match(URL_CORRECTNESS_REGEX, url) is not None





### ENTRYPOINT ###
# Setup the application as a Flask app
app = Flask(__name__)





### API FUNCTIONS ###
# We use a flask macro to make let this function be called for the root URL ("/") and the specified HTTP methods.
@app.route("/", methods=['GET', 'POST', 'DELETE'])
def root():
    """
        Handles everything that falls under the API root (/).

        Supported methods:
         - GET: Returns a list of all the identifiers, as a JSON file.
         - POST: Asks to generate a new ID for the given URL (not in the URL itself, but as a form-parameter).
         - DELETE: Not supported for the general, so will return a 404 always.
    """

    # Switch on the method used
    if request.method == "GET":
        # Collect all the results in a JSON map
        # We can simply return a dict, and flask will automatically serialize this to JSON for us
        return { "keys": [k for k in id_url_map] }

    elif request.method == "POST":
        # Try to get the URL
        if "url" not in request.form:
            return "URL not specified", 400
        url = request.form["url"]

        # Validate the URL
        if not valid_url(url):
            return "Invalid URL", 400

        # Generate a new identifier
        identifier = generate_id()

        # Insert it into the map
        id_url_map[identifier] = url

        # Return it, with the 201 status code
        # When given a tuple, flask will automatically return it as text/status code
        return identifier, 201

    elif request.method == "DELETE":
        # If we have nothing to delete, we return 404 to indicate so
        if not id_url_map: return "Nothing to delete", 404

        # Otherwise, clear the list
        to_remove = list(id_url_map.keys())
        for k in to_remove:
            del id_url_map[k]

        # Return 204, since we deleted everything
        return "success", 204

# We use a flask macro to make let this function be called for any nested string under the root URL ("/:id") and the specified HTTP methods.
# The syntax of the identifier is '<string:id>', which tells flask it's a string (=any non-slash text) that is named 'id'
@app.route("/<string:id>", methods=['GET', 'PUT', 'DELETE'])
def url(id):
    """
        Handles everything that falls under a URL that is an identifier (/:id).

        Methods:
         - GET: Returns the URL behind the given identifier as a 301 result (moved permanently) so the browser automatically redirects.
         - PUT: Updates the given ID to point to the given URL (as a POST field). Returns a 200 on success, 400 on failure or 404 on not-existing ID.
         - DELETE: Deletes the ID/URL mapping based on the ID given, returning a 204 (no content).
    """

    # Switch on the method used
    if request.method == "GET":
        # Check to see if we know this one
        if id in id_url_map:
            # We do! Redirect the user to it
            # The redirect() function will automatically set the correct headers and status code
            return redirect(id_url_map[id])
        else:
            # Resource not found
            abort(404)

    elif request.method == "PUT":
        # Check if we know the ID
        if id not in id_url_map:
            abort(404)

        # Try to get the URL
        if "url" not in request.form:
            return "URL not specified", 400
        url = request.form["url"]

        # Validate the URL
        if not valid_url(url):
            return "Invalid URL", 400

        # Check if we know the ID
        if id not in id_url_map:
            abort(404)

        # Update the ID
        id_url_map[id] = url

        # Done!
        return "success", 200

    elif request.method == "DELETE":
        # Check if it exists
        if id in id_url_map:
            # Remove it, then success
            del id_url_map[id]
            return "success", 204
        else:
            # Resource not found (we found nothing to delete)
            abort(404)
