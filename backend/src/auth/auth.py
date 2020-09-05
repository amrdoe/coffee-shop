import json
from flask import request
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from sys import stderr


AUTH0_DOMAIN = 'amrikhudair.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://coffee-shop.test'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    auth = request.headers.get('Authorization', '')

    if not auth:
        auth_e401(
            'authorization_header_missing',
            'Authorization header is expected.'
        )

    parts = auth.split(' ')

    if len(parts) > 2 or parts[0].lower() != 'bearer':
        auth_e401('invalid_header', 'Authorization header must be bearer token.')

    if len(parts) == 1: auth_e401('invalid_header', 'Token not found.')

    return parts[1]

'''
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        auth_e403('invalid_header', 'Permissions are not defined in token.')
    if permission not in payload['permissions']:
        auth_e403(
            'not_permitted',
            'You don\'t have suffecient permission to perform this action.'
        )

'''
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    header = jwt.get_unverified_header(token)

    if 'kid' not in header:
        auth_e401('invalid_header', 'Authorization is malformed.')

    key = next((k for k in jwks['keys'] if k['kid'] == header['kid']), None)

    if not key:
        auth_e401('invalid_header', 'Unable to find the appropriate key.')

    try:
        return jwt.decode(
            token, key, algorithms=ALGORITHMS,
            audience=API_AUDIENCE, issuer=f'https://{AUTH0_DOMAIN}/'
        )

    except jwt.ExpiredSignatureError:
        auth_e401('token_expired', 'Token Expired')

    except jwt.JWTClaimsError:
        auth_e401(
            'invalid_claims',
            'Incorrect claims. Please, check the audience and issuer.'
        )

    except Exception as e:
        print(e, file=stderr)
        auth_e401('invalid_header', 'Unable to parse authentication token.')

'''
    @INPUTS
        code: the auth error code (string)
        description: the auth error description (string)

    Raises an AuthError with given code and parameter and 401 status
'''
def auth_e401(code, description):
    raise AuthError({ 'code': code, 'description': description }, 401)

'''
    @INPUTS
        code: the auth error code (string)
        description: the auth error description (string)

    Raises an AuthError with given code and parameter and 403 error
'''
def auth_e403(code, description):
    raise AuthError({ 'code': code, 'description': description }, 403)

'''
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(*args, **kwargs)

        return wrapper
    return requires_auth_decorator
