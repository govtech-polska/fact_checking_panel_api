Admin
=====

Endpoints dedicated for users with administrative permissions.

List Experts
------------

.. http:get:: /admin/experts

    Fetches lists of users with expert role.

    :reqheader Authorization: token in format ``Token <token_value>``

    :query string specialization: filtering by user specialization

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

    **Example request**:

    .. http:example:: curl httpie

        GET /admin/experts HTTP/1.1
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

List Fact Checkers
------------------

.. http:get:: /admin/fact-checkers

    Fetches lists of users with fact checker role.

    :reqheader Authorization: token in format ``Token <token_value>``

    :query string specialization: filtering by user specialization

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

    **Example request**:

    .. http:example:: curl httpie

        GET /admin/fact-checkers HTTP/1.1
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

.. http:get:: /admin/invitations

    Fetches lists of user invitations.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>jsonarr string email: user email
    :>jsonarr boolean expired: is invitation expired
    :>jsonarr uuid id: user id
    :>jsonarr datetime sent_at: user created at
    :>jsonarr string status: invitation status

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Example request**:

    .. http:example:: curl httpie

        GET /admin/invitations HTTP/1.1
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

User Details
------------

.. http:get:: /admin/users/(uuid:pk)

    Fetches user details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json string role: user role
    :>json boolean is_active: is user active

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        GET /admin/users/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, OPTIONS
        Content-Type: application/json

        {
            "is_active": true,
            "role": "expert"
        }


User Update
-----------

.. http:patch:: /admin/users/(uuid:pk)

    Updates user details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string role: user role
    :<json boolean is_active: is user active

    :>json string role: user role
    :>json boolean is_active: is user active

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        PATCH /admin/users/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "is_active": false,
            "role": "expert"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, OPTIONS
        Content-Type: application/json

        {
            "is_active": false,
            "role": "expert"
        }

News List
---------

.. http:get:: /admin/news

    Fetches list of news.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>jsonarr uuid id: news id
    :>jsonarr string comment: news comment
    :>jsonarr string current_verdict: news current verdict
    :>jsonarr boolean deleted: is news deleted
    :>jsonarr boolean is_duplicate: is news duplicated
    :>jsonarr boolean is_sensitive: is news sensitive
    :>jsonarr list newssensitivekeyword_set: list of sensitive keywords
    :>jsonarr datetime reported_at: news reported at
    :>jsonarr string screenshot_url: news url
    :>jsonarr string text: news text
    :>jsonarr string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions


    **Example request**:

    .. http:example:: curl httpie

        GET /admin/news HTTP/1.1
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
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "comment": "test_comment",
                    "current_verdict": "no_verdict",
                    "deleted": false,
                    "is_duplicate": false,
                    "is_sensitive": true,
                    "newssensitivekeyword_set": [
                        "sensitive_keyword"
                    ],
                    "screenshot_url": "www.some_screenshot.url",
                    "text": "test_text",
                    "url": "www.some.url",
                }
            ],
            "total": 1
        }

News Detail
-----------

.. http:get:: /admin/news/(uuid:pk)

    Fetches news details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json uuid id: news id
    :>json string comment: news comment
    :>json string current_verdict: news current verdict
    :>json boolean deleted: is news deleted
    :>json boolean is_duplicate: is news duplicated
    :>json boolean is_sensitive: is news sensitive
    :>json list newssensitivekeyword_set: list of sensitive keywords
    :>json datetime reported_at: news reported at
    :>json string screenshot_url: news url
    :>json string text: news text
    :>json string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist


    **Example request**:

    .. http:example:: curl httpie

        GET /admin/news/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, OPTIONS
        Content-Type: application/json

        {
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "comment": "test_comment",
            "current_verdict": "no_verdict",
            "deleted": false,
            "is_duplicate": false,
            "is_sensitive": true,
            "newssensitivekeyword_set": [
                "sensitive_keyword"
            ],
            "screenshot_url": "www.some_screenshot.url",
            "text": "test_text",
            "url": "www.some.url",
        }

News Update
-----------

.. http:get:: /admin/news/(uuid:pk)

    Updates news.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string comment: news comment
    :<json boolean deleted: is news deleted
    :<json string url: news url
    :<json string text: news text

    :>json string comment: news comment
    :>json boolean deleted: is news deleted
    :>json string url: news url
    :>json string text: news text

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        PATCH /admin/news/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "comment": "test_update_comment",
            "deleted": true,
            "text": "test_update_text",
            "url": "www.some_updated.url"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, OPTIONS
        Content-Type: application/json

        {
            "comment": "test_update_comment",
            "deleted": true,
            "text": "test_update_text",
            "url": "www.some_updated.url"
        }

News Add Screenshot
-------------------

.. http:patch:: /admin/news-image/(uuid:pk)

    Updates news with given screenshot.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<multipart bytes image: image file

    :statuscode 204: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist
    :statuscode 503: storage service unavailable

Keywords List
-------------

.. http:get:: /admin/keywords

    Fetches list of sensitive keywords.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>jsonarr uuid id: keyword id
    :>jsonarr datetime created_at: keyword created datetime
    :>jsonarr string name: keyword name

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Example request**:

    .. http:example:: curl httpie

        GET /admin/keywords HTTP/1.1
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

Keyword Create
--------------

.. http:post:: /admin/keywords

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

    **Example request**:

    .. http:example:: curl httpie

        POST /admin/keywords HTTP/1.1
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

Keyword Detail
--------------

.. http:get:: /admin/keywords/(uuid:pk)

    Fetches sensitive keyword details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json uuid id: keyword id
    :>json datetime created_at: keyword created datetime
    :>json string name: keyword name

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        GET /admin/keywords/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
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

Keyword Update
--------------

.. http:patch:: /admin/keywords/(uuid:pk)

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

    **Example request**:

    .. http:example:: curl httpie

        PATCH /admin/keywords/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
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

Keyword Delete
--------------

.. http:delete:: /admin/keywords/(uuid:pk)

    Deletes sensitive keyword.

    :reqheader Authorization: token in format ``Token <token_value>``

    :statuscode 204: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        DELETE /admin/keywords/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Allow: GET, PATCH, DELETE, OPTIONS
        Content-Type: application/json

Expert Opinion Update
---------------------

.. http:put:: /admin/expert-opinion/(int:pk)

    Updates expert opinion.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json boolean about_corona_virus: is news about corona virus
    :<json string comment: comment
    :<json string confirmation_sources: confirmation sources
    :<json string duplicate_reference: news duplicate reference
    :<json boolean is_duplicate: is new duplicated
    :<json string title: title
    :<json string verdict: verdict

    :>json boolean about_corona_virus: is news about corona virus
    :>json string comment: comment
    :>json string confirmation_sources: confirmation sources
    :>json string duplicate_reference: news duplicate reference
    :>json int id: opinion id
    :>json boolean is_duplicate: is new duplicated
    :>json object judge: author of opinion
    :>json string title: title
    :>json string verdict: verdict

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        PUT /admin/expert-opinion/1 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "about_corona_virus": true,
            "comment": "Thinking through all the facts and other dependencies, yes.",
            "confirmation_sources": "drop.com",
            "duplicate_reference": null,
            "is_duplicate": false,
            "title": "Some random title",
            "verdict": true
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: PUT, OPTIONS
        Content-Type: application/json

        {
            "about_corona_virus": true,
            "comment": "Thinking through all the facts and other dependencies, yes.",
            "confirmation_sources": "drop.com",
            "duplicate_reference": null,
            "id": 1,
            "is_duplicate": false,
            "judge": {
                "id": "9c79bfe1-6b15-4ccf-b4f0-266c631fa480",
                "email": "test@email.com",
                "name": "judge_name"
            },
            "title": "Some random title",
            "verdict": true
        }

Fact Checker Opinion Update
---------------------------

.. http:put:: /admin/fact-checker-opinion/(int:pk)

    Updates fact checker opinion.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json boolean about_corona_virus: is news about corona virus
    :<json string comment: comment
    :<json string confirmation_sources: confirmation sources
    :<json string duplicate_reference: news duplicate reference
    :<json boolean is_duplicate: is new duplicated
    :<json string title: title
    :<json string verdict: verdict

    :>json boolean about_corona_virus: is news about corona virus
    :>json string comment: comment
    :>json string confirmation_sources: confirmation sources
    :>json string duplicate_reference: news duplicate reference
    :>json int id: opinion id
    :>json boolean is_duplicate: is new duplicated
    :>json object judge: author of opinion
    :>json string title: title
    :>json string verdict: verdict

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        PUT /admin/fact-checker-opinion/1 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "about_corona_virus": true,
            "comment": "Thinking through all the facts and other dependencies, yes.",
            "confirmation_sources": "drop.com",
            "duplicate_reference": null,
            "is_duplicate": false,
            "title": "Some random title",
            "verdict": true
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: PUT, OPTIONS
        Content-Type: application/json

        {
            "about_corona_virus": true,
            "comment": "Thinking through all the facts and other dependencies, yes.",
            "confirmation_sources": "drop.com",
            "duplicate_reference": null,
            "id": 1,
            "is_duplicate": false,
            "judge": {
                "id": "9c79bfe1-6b15-4ccf-b4f0-266c631fa480",
                "email": "test@email.com",
                "name": "judge_name"
            },
            "title": "Some random title",
            "verdict": true
        }
