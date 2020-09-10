Users
=====

Endpoints related to users management.


User Details
------------

.. http:get:: /users/(uuid:pk)

    Fetches user details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json object domain: associated domain
    :>json string email: user email
    :>json boolean is_active: is user active
    :>json string name: user name
    :>json string role: user role
    :>json string specialization: user role

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``

    **Example request**:

    .. http:example:: curl httpie

        GET /users/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, OPTIONS
        Content-Type: application/json

        {
             "domain": {
                "created_at": "2020-05-11T05:04:14.943309Z",
                "id": "aaaccefb-b122-4fe8-aab2-cf6061da20a7",
                "name": "test_domain"
            },
            "email": "email@test.com",
            "is_active": true,
            "name": "test_name",
            "role": "specialist",
            "specialization": "other"
        }

User Update
-----------

.. http:patch:: /users/(uuid:pk)

    Updates user details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json uuid domain: associated domain
    :<json string name: user name
    :<json string role: user role
    :<json string specialization: user specialization
    :<json boolean is_active: is user active

    :>json object domain: associated domain
    :>json string email: user email
    :>json boolean is_active: is user active
    :>json string name: user name
    :>json string role: user role
    :>json string specialization: user role

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``

    **Example request**:

    .. http:example:: curl httpie

        PATCH /users/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "is_active": false,
            "name": "updated_name"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, OPTIONS
        Content-Type: application/json

        {
             "domain": {
                "created_at": "2020-05-11T05:04:14.943309Z",
                "id": "aaaccefb-b122-4fe8-aab2-cf6061da20a7",
                "name": "test_domain"
            },
            "email": "email@test.com",
            "is_active": false,
            "name": "updated_name",
            "role": "specialist",
            "specialization": "other"
        }


List Moderators
---------------

.. http:get:: /users/moderators

    Fetches lists of users with moderator role.

    :reqheader Authorization: token in format ``Token <token_value>``

    :query string search: filtering by name or email
    :query string specialization: filtering by user specialization
    :query datetime created_after: filtering by user appearance in the system after given date
    :query datetime created_before: filtering by user appearance in the system before given date
    :query boolean is_active: filtering active/inactive users
    :query string ordering: ordering by field; supported fields: ``name, -name, verified, -verified, created_at -created_at``

    :>jsonarr datetime created_at: user created at
    :>jsonarr string email: user email
    :>jsonarr uuid id: user id
    :>jsonarr boolean is_active: is user active
    :>jsonarr string name: user name
    :>jsonarr string specialization: user role

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Allowed for user roles:**

    ``admin``

    **Example request**:

    .. http:example:: curl httpie

        GET /users/moderators HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "current_page": 1,
            "page_size": 20,
            "results": [
               {
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "email": "email@test.com",
                    "id": "aaaccefb-b122-4fe8-aab2-cf6061da20a7",
                    "is_active": true,
                    "name": "test_name",
                    "specialization": "other"
                }
            ],
            "total": 1
        }


List Experts
------------

.. http:get:: /users/experts

    Fetches lists of users with expert role.

    :reqheader Authorization: token in format ``Token <token_value>``

    :query string search: filtering by name or email
    :query string specialization: filtering by user specialization
    :query datetime created_after: filtering by user appearance in the system after given date
    :query datetime created_before: filtering by user appearance in the system before given date
    :query boolean is_active: filtering active/inactive users
    :query string ordering: ordering by field; supported fields: ``name, -name, assigned, -assigned, verified, -verified, created_at -created_at``

    :>jsonarr int assigned: user assigned
    :>jsonarr datetime created_at: user created at
    :>jsonarr object domain: associated domain (null)
    :>jsonarr string email: user email
    :>jsonarr uuid id: user id
    :>jsonarr boolean is_verified: is user verified
    :>jsonarr string name: user name
    :>jsonarr string specialization: user specialization
    :>jsonarr int verified: user verified

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        GET /users/experts HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "current_page": 1,
            "page_size": 20,
            "results": [
                {
                    "assigned": 0,
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "domain": null,
                    "email": "email@test.com",
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "is_active": true,
                    "name": "test_name",
                    "specialization": "other",
                    "verified": 1
                }
            ],
            "total": 1
        }

List Specialists
----------------

.. http:get:: /users/specialists

    Fetches lists of users with specialist role.

    :reqheader Authorization: token in format ``Token <token_value>``

    :query string search: filtering by name or email
    :query string domain: filtering by specialist domain
    :query string specialization: filtering by user specialization
    :query datetime created_after: filtering by user appearance in the system after given date
    :query datetime created_before: filtering by user appearance in the system before given date
    :query boolean is_active: filtering active/inactive users
    :query string ordering: ordering by field; supported fields: ``name, -name, assigned, -assigned, verified, -verified, created_at -created_at``

    :>jsonarr int assigned: user assigned
    :>jsonarr datetime created_at: user created at
    :>jsonarr object domain: associated domain
    :>jsonarr string email: user email
    :>jsonarr uuid id: user id
    :>jsonarr boolean is_verified: is user verified
    :>jsonarr string name: user name
    :>jsonarr string specialization: user specialization
    :>jsonarr int verified: user verified

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: domain does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        GET /users/specialists HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "current_page": 1,
            "page_size": 20,
            "results": [
                {
                    "assigned": 0,
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "domain": {
                        "created_at": "2020-05-11T05:04:14.943309Z",
                        "id": "aaaccefb-b122-4fe8-aab2-cf6061da20a7",
                        "name": "test_domain"
                    },
                    "email": "email@test.com",
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "is_active": true,
                    "name": "test_name",
                    "specialization": "other",
                    "verified": 1
                }
            ],
            "total": 1
        }

List Fact Checkers
------------------

.. http:get:: /users/fact-checkers

    Fetches lists of users with fact checker role.

    :reqheader Authorization: token in format ``Token <token_value>``

    :query string search: filtering by name or email
    :query string specialization: filtering by user specialization
    :query datetime created_after: filtering by user appearance in the system after given date
    :query datetime created_before: filtering by user appearance in the system before given date
    :query boolean is_active: filtering active/inactive users
    :query string ordering: ordering by field; supported fields: ``name, -name, assigned, -assigned, verified, -verified, created_at -created_at``

    :>jsonarr int assigned: user assigned
    :>jsonarr datetime created_at: user created at
    :>jsonarr string email: user email
    :>jsonarr uuid id: user id
    :>jsonarr boolean is_verified: is user verified
    :>jsonarr string name: user name
    :>jsonarr string specialization: user specialization
    :>jsonarr int verified: user verified

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Allowed for user roles:**

    ``admin``

    **Example request**:

    .. http:example:: curl httpie

        GET /users/fact-checkers HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "current_page": 1,
            "page_size": 20,
            "results": [
                {
                    "assigned": 0,
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "email": "email@test.com",
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "is_active": true,
                    "name": "test_name",
                    "specialization": "other",
                    "verified": 1
                }
            ],
            "total": 1
        }

List Invitations
----------------

.. http:get:: /users/invitations

    Fetches lists of user invitations.

    :reqheader Authorization: token in format ``Token <token_value>``

    :query string status: filtering by invitation status from values ``failed, waiting, in_progress, used``
    :query boolean is_expired: filtering by expired invitations
    :query string ordering: ordering by field; supported fields: ``sent_at, -sent_at``

    :>jsonarr string email: user email
    :>jsonarr boolean expired: is invitation expired
    :>jsonarr uuid id: user id
    :>jsonarr datetime sent_at: user created at
    :>jsonarr string status: invitation status

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Allowed for user roles:**

    ``admin``

    **Example request**:

    .. http:example:: curl httpie

        GET /users/invitations HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "current_page": 1,
            "page_size": 20,
            "results": [
                {
                    "email": "email@test.com",
                    "expired": false,
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "sent_at": "2020-05-11T05:04:14.943309Z",
                    "status": "Waiting"
                }
            ],
            "total": 1
        }

Edit Subscriptions
------------------

.. http:patch:: /users/allow-subscriptions

    Enabled/disables subscriptions for requesting user.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json boolean allow_subscriptions: flag indicating subscription agreement

    :statuscode 204: success
    :statuscode 401: not authorized

    **Example request**:

    .. http:example:: curl httpie

        PATCH /users/allow-subscriptions HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "allow_subscriptions": false
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Allow: PATCH, OPTIONS
        Content-Type: application/json
