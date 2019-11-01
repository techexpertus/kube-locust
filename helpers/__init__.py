import sys

import jwt

def logOnError(response):
    req = response.request
    """
    Ignore this function for now, but potentially could be used for debugging script as locust script cannot be debugged in IDE
    """
    print('\n{}\n{}\n{}\n\n{}'.format(
        '-----------Request-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

    print('\n{}\n{}\n{}\n\n{}'.format(
        '-----------Response-----------',
        'Response code:' + str(response.status_code),
        '\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
        response.text,
    ))


def post_headers():
    token = getJWTToken()
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }


def is_master():
    return '--master' in sys.argv


def is_slave():
    return '--slave' in sys.argv


def getTargetHost():
    # return os.environ['TARGET_HOST']
    toreturn = False
    for arg in sys.argv:
        if toreturn:
            return arg
        if arg == '-H' or arg == '--host':
            toreturn = True
    return "error"
