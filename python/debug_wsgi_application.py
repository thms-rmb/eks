import io
import pdb
import sys

from werkzeug.datastructures import Headers
from werkzeug.test import create_environ, run_wsgi_app

# invenio.webstyle.webinterface_handler_wsgi re-assigns stdout, so we have to
# assign it back in order for pdb to work properly in python3.
sys_stdout = sys.stdout
from invenio.webstyle.webinterface_handler_wsgi import application
sys.stdout = sys_stdout


PATH = "/circulation/get_checkout_patron_info/1000251/"
QUERY_STRING = {
}

DATA = {
}

METHOD = "GET"
COOKIE = ""


def do_run_debug():
    headers = Headers()
    if COOKIE:
        headers.add("Cookie", "INVENIOSESSION={}".format(COOKIE))

    environ = create_environ(
        path=PATH,
        query_string=QUERY_STRING,
        data=DATA,
        method=METHOD,
        headers=headers,
        environ_overrides={
            "wsgi.url_scheme": "https",
            "REMOTE_ADDR": "84.202.138.58",
        },
    )

    app_iter, status, headers = run_wsgi_app(application, environ)

    return b"".join(app_iter), status, headers


pdb.runcall(do_run_debug)
