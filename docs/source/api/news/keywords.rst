Keywords
========

Endpoints related to keywords management.

Sensitive Keywords List
-----------------------

.. http:get:: /news/keywords/sensitive

    Fetches list of sensitive keywords.

    :reqheader Authorization: token in format ``Token <token_value>``

    :query string search: search query (across ``name`` field)

    :>jsonarr uuid id: keyword id
    :>jsonarr datetime created_at: keyword created datetime
    :>jsonarr string name: keyword name

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        GET /news/keywords/sensitive HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, OPTIONS
        Content-Type: application/json

        {
            "current_page": 1,
            "page_size": 20,
            "results": [
                {
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "name": "test_name"
                },
                {
                    "id": "12bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "created_at": "2020-04-11T05:04:14.943309Z",
                    "name": "test_name_2"
                }
            ],
            "total": 2
        }

Sensitive Keyword Create
------------------------

.. http:post:: /news/keywords/sensitive

    Creates a sensitive keyword.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string name: keyword name

    :>json uuid id: keyword id
    :>json datetime created_at: keyword created datetime
    :>json string name: keyword name

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        POST /news/keywords/sensitive HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "name": "test_create_name"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, OPTIONS
        Content-Type: application/json

        {
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "created_at": "2020-05-11T05:04:14.943309Z",
            "name": "test_create_name"
        }


Sensitive Keyword Detail
------------------------

.. http:get:: /news/keywords/sensitive/(uuid:pk)

    Fetches sensitive keyword details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json uuid id: keyword id
    :>json datetime created_at: keyword created datetime
    :>json string name: keyword name

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        GET /news/keywords/sensitive/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, DELETE, OPTIONS
        Content-Type: application/json

        {
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "created_at": "2020-05-11T05:04:14.943309Z",
            "name": "test_name"
        }

Sensitive Keyword Update
------------------------

.. http:patch:: /news/keywords/sensitive/(uuid:pk)

    Updates sensitive keyword details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string name: keyword name

    :>json uuid id: keyword id
    :>json datetime created_at: keyword created datetime
    :>json string name: keyword name

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        PATCH /news/keywords/sensitive/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "name": "test_update_name"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, DELETE, OPTIONS
        Content-Type: application/json

        {
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "created_at": "2020-05-11T05:04:14.943309Z",
            "name": "test_update_name"
        }

Sensitive Keyword Delete
------------------------

.. http:delete:: /news/keywords/sensitive/(uuid:pk)

    Deletes sensitive keyword.

    :reqheader Authorization: token in format ``Token <token_value>``

    :statuscode 204: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        DELETE /news/keywords/sensitive/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Allow: GET, PATCH, DELETE, OPTIONS
        Content-Type: application/json

Domain List
-----------

.. http:get:: /news/keywords/domains

    Fetches list of domains.

    :query string search: search query (across ``name`` field)

    :>jsonarr uuid id: domain id
    :>jsonarr datetime created_at: domain created datetime
    :>jsonarr string name: domain name

    :statuscode 200: success

    **Example request**:

    .. http:example:: curl httpie

        GET /news/keywords/domains HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, OPTIONS
        Content-Type: application/json

        {
            "current_page": 1,
            "page_size": 20,
            "results": [
                {
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "name": "test_name"
                },
                {
                    "id": "12bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "created_at": "2020-04-11T05:04:14.943309Z",
                    "name": "test_name_2"
                }
            ],
            "total": 2
        }

Domain Create
-------------

.. http:post:: /news/keywords/domains

    Creates a domain.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string name: domain name

    :>json uuid id: domain id
    :>json datetime created_at: domain created datetime
    :>json string name: domain name

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        POST /news/keywords/domains HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "name": "test_create_name"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, OPTIONS
        Content-Type: application/json

        {
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "created_at": "2020-05-11T05:04:14.943309Z",
            "name": "test_create_name"
        }

Domain Detail
-------------

.. http:get:: /news/keywords/domains/(uuid:pk)

    Fetches domain details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json uuid id: domain id
    :>json datetime created_at: domain created datetime
    :>json string name: domain name

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``
    ``expert``
    ``specialist``
    ``fact_checker``

    **Example request**:

    .. http:example:: curl httpie

        GET /news/keywords/domains/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, DELETE, OPTIONS
        Content-Type: application/json

        {
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "created_at": "2020-05-11T05:04:14.943309Z",
            "name": "test_name"
        }

Domain Update
-------------

.. http:patch:: /news/keywords/domains/(uuid:pk)

    Updates domain details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string name: keyword name

    :>json uuid id: domain id
    :>json datetime created_at: domain created datetime
    :>json string name: domain name

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        PATCH /news/keywords/domains/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "name": "test_update_name"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, DELETE, OPTIONS
        Content-Type: application/json

        {
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "created_at": "2020-05-11T05:04:14.943309Z",
            "name": "test_update_name"
        }

Domain Delete
-------------

.. http:delete:: /news/keywords/domains/(uuid:pk)

    Deletes domain.

    :reqheader Authorization: token in format ``Token <token_value>``

    :statuscode 204: success
    :statuscode 400: can not delete domain associated to user
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        DELETE /news/keywords/domains/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Allow: GET, PATCH, DELETE, OPTIONS
        Content-Type: application/json

Tag List
--------

.. http:get:: /news/keywords/tags

    Fetches list of tags.

    :query boolean popular: sort by popularity
    :query string search: search query (across ``name`` field)

    :>jsonarr uuid id: tag id
    :>jsonarr datetime created_at: tag created datetime
    :>jsonarr string name: tag name

    :statuscode 200: success

    **Example request**:

    .. http:example:: curl httpie

        GET /news/keywords/tags HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, OPTIONS
        Content-Type: application/json

        {
            "current_page": 1,
            "page_size": 20,
            "results": [
                {
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "name": "test_name"
                },
                {
                    "id": "12bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "created_at": "2020-04-11T05:04:14.943309Z",
                    "name": "test_name_2"
                }
            ],
            "total": 2
        }

Tag Create
----------

.. http:post:: /news/keywords/tags

    Creates a tag.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string name: tag name

    :>json uuid id: tag id
    :>json datetime created_at: tag created datetime
    :>json string name: tag name

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Allowed for user roles:**

    ``admin``
    ``moderator``
    ``expert``
    ``specialist``

    **Example request**:

    .. http:example:: curl httpie

        POST /news/keywords/tags HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "name": "test_create_name"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, OPTIONS
        Content-Type: application/json

        {
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "created_at": "2020-05-11T05:04:14.943309Z",
            "name": "test_create_name"
        }

Tag Detail
----------

.. http:get:: /news/keywords/tags/(uuid:pk)

    Fetches tag details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json uuid id: tag id
    :>json datetime created_at: tag created datetime
    :>json string name: tag name

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``
    ``expert``
    ``specialist``
    ``fact_checker``

    **Example request**:

    .. http:example:: curl httpie

        GET /news/keywords/tags/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, DELETE, OPTIONS
        Content-Type: application/json

        {
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "created_at": "2020-05-11T05:04:14.943309Z",
            "name": "test_name"
        }

Tag Update
----------

.. http:patch:: /news/keywords/tags/(uuid:pk)

    Updates tag details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string name: tag name

    :>json uuid id: tag id
    :>json datetime created_at: tag created datetime
    :>json string name: tag name

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        PATCH /news/keywords/tags/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "name": "test_update_name"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, DELETE, OPTIONS
        Content-Type: application/json

        {
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "created_at": "2020-05-11T05:04:14.943309Z",
            "name": "test_update_name"
        }

Tag Delete
----------

.. http:delete:: /news/keywords/tags/(uuid:pk)

    Deletes tag.

    :reqheader Authorization: token in format ``Token <token_value>``

    :statuscode 204: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        DELETE /news/keywords/tags/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Allow: GET, PATCH, DELETE, OPTIONS
        Content-Type: application/json
