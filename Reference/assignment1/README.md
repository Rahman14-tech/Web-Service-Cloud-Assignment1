# Web Services and Cloud-Based Systems - Assignment 1
This is the reference implementation for the first assignment of the Web Services and Cloud-Based Systems course.

## Installation
To setup your machine to run the simple URL-shortener REST-service, first prepare your machine by setting up a virtual environment with the required packages:
```bash
# Setup the virtual environment locally
python3 -m venv ./venv
# Activate it for your current terminal
. venv/bin/activate
# Your terminal now has '(venv)' prepended to the prompt

# Install the dependencies
pip3 install flask
```

You are now ready to run the service.


## Usage
### Starting the service
To run the service, first make sure you have activated the virtual environment (it has to say 'venv' at the start of your terminal):
```bash
. venv/bin/activate
# Your terminal now has '(venv)' prepended to the prompt
```

Then, run the flask service:
```bash
FLASK_APP=src/url-shortener python3 -m flask run
```
This will launch the service on the default port (`5000`). To run it on another port instead (e.g., `8000`), use the `--port` option:
```bash
FLASK_APP=src/url-shortener python3 -m flask run --port 8080
```


### Using the service
The service implements a few methods, which we will describe here. While this should align with the specification in the assignment, it might differ from how you have designed the methods; that's perfectly fine! They are left purposefully vague so you have some freedom during the assignment.

The methods that we have implemented:
- `/` GET: Returns all the keys currently registered in the URL-shortener services as a JSON file.
    - Returns `200` (OK) and a JSON file of the following form on success:
      ```json
      {
          "keys": [ "key1", "key2", ... ]
      }
      ```
      Note that the list might be empty.
- `/` POST: Creates a new, shortened URL for the given URL by generating a new key. Requires a `url` field with the URL to add.
    - Returns `201` (Created) and the new key on success.
    - Returns `400` (Bad request) with the reason if something went wrong (no `url`-field given or the `url` is not validated correctly).
- `/` DELETE: Deletes all keys in the shortener.
    - Returns `204` (No content) if at least one key was deleted.
    - Returns `404` (Not found) if there was nothing to delete.
- `/:id` GET: Returns the long URL behind the shortened URL by redirecting the web browser.
    - Returns `301` (Moved permanently) with the long URL to redirect the browser.
    - Returns `404` (Not found) if there is no such shortened URL.
- `/:id` PUT: Updates the given ID with a new URL, stored in a `url`-field.
    - Returns `200` (OK) if the update was successfull.
    - Returns `400` (Bad request) with the reason why if something went wrong (no `url`-field given or the `url` is not validated correctly).
    - Returns `404` (Not found) if there is no such shortened URL.
- `/:id` DELETE: Deletes the given ID.
    - Returns `204` (No content) if the removal was successfull.
    - Returns `404` (Not found) if there is no such shortened URL.


## Documentation
The whole service is implemented in `src/url-shortener.py`, which includes comments that explain what does what. We recommend to take a look there if you want to understand the how the service works.
