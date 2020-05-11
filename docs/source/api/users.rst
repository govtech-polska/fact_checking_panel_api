Users
=====

Endpoints related to accounts management.

Sign Up
-------

..  http:post:: /users/login/(uuid:token)

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

        POST /users/sign-up HTTP/1.1
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

..  http:post:: /users/login

    Logs user to the system given valid credentials.

    :<json string email: user email
    :<json string password: user password

    :>json uuid token: authentication token

    :statuscode 200: success
    :statuscode 400: invalid credentials
    :statuscode 401: user not verified

    **Example request**:

    .. http:example:: curl httpie

        POST /users/login HTTP/1.1
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


Send Invite
-----------

.. http:post:: /users/send-invite

    Sends invitation email to a user email with created verification token.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string email: user email
    :<json string user_role: user role

    :>json string email: user email
    :>json string user_role: user role

    :statuscode 201: success
    :statuscode 400: invitation with given email already exists
    :statuscode 401: not authorized
    :statuscode 503: internal email service error

    **Example request**:

    .. http:example:: curl httpie

        POST /users/send-invite HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "email": "email@test.com",
            "user_role": "expert"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: POST, OPTIONS
        Content-Type: application/json

        {
            "email": "email@test.com",
            "user_role": "expert"
        }


Current User
------------

.. http:get:: /users/current-user

    Fetches requesting user details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json string email: user email
    :>json string name: user email
    :>json string user_role: user role

    :statuscode 200: success
    :statuscode 401: not authorized

    **Example request**:

    .. http:example:: curl httpie

        GET /users/current-user HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "email": "email@test.com",
            "name": "test_name",
            "user_role": "expert"
        }


Password Reset Request
----------------------

.. http:post:: /users/reset-password-request

    Sends password reset credentials to requesting user email address.

    :<json string email: user email

    :statuscode 200: success
    :statuscode 503: internal email service error

    **Example request**:

    .. http:example:: curl httpie

        POST /users/reset-password-request HTTP/1.1
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

.. http:post:: /users/reset-password/(uuid:uidb64)/(uuid:token)

    Resets user password given password reset credentials.

    :<json string password: new password
    :<json string password2: new password

    :statuscode 200: success
    :statuscode 400: user does not exist, invalid token

    **Example request**:

    .. http:example:: curl httpie

        POST /users/reset-password/<uidb64_value_here>/<token_value_here> HTTP/1.1
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

.. http:post:: /users/internal-reset-password

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

        POST /users/internal-reset-password HTTP/1.1
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