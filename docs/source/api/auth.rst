Auth
====

Endpoints related to accounts management.

Sign Up
-------

..  http:post:: /auth/login/(uuid:token)

    Registers a user given a valid invitation token.

    :<json string name: user name
    :<json string password: user password
    :<json string password2: user password repeated
    :<json string specialization: user specialization

    :>json string name: user name
    :>json string email: user email
    :>json string role: user role
    :>json string specialization: user specialization

    :statuscode 201: success
    :statuscode 400: token invalid, token already used, internal registration error, password too weak

    **Example request**:

    .. http:example:: curl httpie

        POST /auth/sign-up HTTP/1.1
        Content-Type: application/json

        {
            "name": "test_user",
            "password": "Test1234!",
            "password2": "Test1234!",
            "specialization": "other"
        }

     **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json

        {
            "email": "test@email.com",
            "name": "test_user",
            "role": "fact_checker",
            "specialization": "other"
        }

Login
-----

..  http:post:: /auth/login

    Logs user to the system given valid credentials. Each time user logs in token is refreshed.

    :<json string email: user email
    :<json string password: user password

    :>json uuid token: authentication token

    :statuscode 200: success
    :statuscode 400: invalid credentials
    :statuscode 401: user not verified

    **Example request**:

    .. http:example:: curl httpie

        POST /auth/login HTTP/1.1
        Content-Type: application/json

        {
            "email": "email@test.com",
            "password": "test_password"
        }

     **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: POST, OPTIONS
        Content-Type: application/json

        {
            "token": "f3803fcbebe81715e434a70be0df06efbf92676f"
        }

Logout
------

..  http:post:: /auth/logout

    Logs a logged in user out from the system.

    :statuscode 204: success
    :statuscode 401: not authorized

    **Example request**:

    .. http:example:: curl httpie

        POST /auth/logout HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Allow: POST, OPTIONS

Send Invite
-----------

.. http:post:: /auth/send-invite

    Sends invitation email to a user email with created verification token.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string email: user email
    :<json string user_role: user role
    :<json uuid domain: required when sending invitation to ``specialists`` (optional)

    :>json string email: user email
    :>json string user_role: user role
    :>json object domain: domain object (null for roles other than ``specialist``)

    :statuscode 201: success
    :statuscode 400: invitation with given email already exists
    :statuscode 401: not authorized
    :statuscode 503: internal email service error

    **Allowed for user roles:**

    ``admin``

    **Example request**:

    .. http:example:: curl httpie

        POST /auth/send-invite HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "email": "email@test.com",
            "user_role": "expert",
            "domain": "52bccefb-b122-4fe8-aab2-cf6061da20a7"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 201 CREATED
        Allow: POST, OPTIONS
        Content-Type: application/json

        {
            "email": "email@test.com",
            "user_role": "expert",
            "domain": {
                "created_at": "2020-05-11T05:04:14.943309Z",
                "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                "name": "test_domain"
            }
        }


Current User
------------

.. http:get:: /auth/current-user

    Fetches requesting user details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json boolean allow_subscriptions: user agreement for subscriptions
    :>json string email: user email
    :>json string name: user email
    :>json string user_role: user role

    :statuscode 200: success
    :statuscode 401: not authorized

    **Example request**:

    .. http:example:: curl httpie

        GET /auth/current-user HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "allow_subscriptions": true,
            "email": "email@test.com",
            "name": "test_name",
            "user_role": "expert"
        }


Password Reset Request
----------------------

.. http:post:: /auth/reset-password-request

    Sends password reset credentials to requesting user email address.

    :<json string email: user email

    :statuscode 200: success
    :statuscode 503: internal email service error

    **Example request**:

    .. http:example:: curl httpie

        POST /auth/reset-password-request HTTP/1.1
        Content-Type: application/json

        {
            "email": "email@test.com"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: POST, OPTIONS
        Content-Type: application/json

        {
            "detail": "Check provided email address for further instructions."
        }


Password Reset
--------------

.. http:post:: /auth/reset-password/(uuid:uidb64)/(uuid:token)

    Resets user password given password reset credentials.

    :<json string password: new password
    :<json string password2: new password

    :statuscode 200: success
    :statuscode 400: user does not exist, invalid token

    **Example request**:

    .. http:example:: curl httpie

        POST /auth/reset-password/<uidb64_value_here>/<token_value_here> HTTP/1.1
        Content-Type: application/json

        {
            "email": "email@test.com"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, OPTIONS
        Content-Type: application/json

        {
            "detail": "Your password has been reset successfully."
        }


Internal Password Reset
-----------------------

.. http:post:: /auth/internal-reset-password

    Resets user password.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string old_password: old password
    :<json string password: new password
    :<json string password2: new password

    :statuscode 200: success
    :statuscode 400: password too weak
    :statuscode 401: not authorized

    **Example request**:

    .. http:example:: curl httpie

        POST /auth/internal-reset-password HTTP/1.1
        Content-Type: application/json

        {
            "old_password": "test_old_password",
            "password": "Test_password123#",
            "password2": "Test_password123#"
        }

     **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: POST, OPTIONS
        Content-Type: application/json

        {
            "detail": "Your password has been reset successfully."
        }