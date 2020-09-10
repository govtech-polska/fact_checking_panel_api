Management
==========

Endpoints related to news administrative management.

News List
---------

.. http:get:: news/management/news

    Fetches list of news. Ordering of results is conducted by ``reported_at``.

    :reqheader Authorization: token in format ``Token <token_value>``

    :query string current_verdict: filtering by verdict from ``true, false, spam, unidentified, no_verdict, dispute``
    :query boolean deleted: filtering deleted items
    :query list domains[]: filtering by a list of domain names
    :query boolean is_duplicate: filtering duplicate items
    :query boolean is_pinned: filtering pinned items
    :query boolean is_published: filtering by published news
    :query boolean is_sensitive: filtering sensitive items
    :query boolean is_verified_by_expert: filtering by news verified by expert
    :query string origin: filtering by news origin from ``plugin, chatbot, mobile``
    :query string search: search filter (by ``text`` field)
    :query list tags[]: filtering by a list of tag names

    :>jsonarr string assigned_crew_member: assigned crew member email
    :>jsonarr string comment: news comment
    :>jsonarr string current_verdict: news current verdict
    :>jsonarr boolean deleted: is news deleted
    :>jsonarr list domains: list of domains
    :>jsonarr object expert_opinion: expert opinion
    :>jsonarr list fact_checker_opinions: list of fact checker opinions
    :>jsonarr uuid id: news id
    :>jsonarr boolean is_duplicate: is news duplicated
    :>jsonarr boolean is_pinned: is news pinned
    :>jsonarr boolean is_published: is news published
    :>jsonarr boolean is_sensitive: is news sensitive
    :>jsonarr string origin: news origin
    :>jsonarr datetime reported_at: news reported at
    :>jsonarr list sensitive_keywords: list of sensitive keywords
    :>jsonarr string screenshot_url: news url
    :>jsonarr list tags: list of tags
    :>jsonarr string text: news text
    :>jsonarr string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        GET /news/management/news HTTP/1.1
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
                    "assigned_crew_member": "test@crew.com",
                    "comment": "test_comment",
                    "current_verdict": "no_verdict",
                    "deleted": false,
                    "domains": [
                        {
                            "created_at": "2020-05-11T05:04:14.943309Z",
                            "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                            "name": "test_name"
                        }
                    ],
                    "expert_opinion": null,
                    "fact_checker_opinions": [],
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "is_duplicate": false,
                    "is_pinned": true,
                    "is_published": true,
                    "is_sensitive": true,
                    "origin": "plugin",
                    "reported_at": "2020-06-05T11:27:11.886109Z",
                    "screenshot_url": "www.some_screenshot.url",
                    "sensitive_keywords": [
                        "sensitive_keyword"
                    ],
                    "tags": [
                        {
                            "created_at": "2020-05-11T05:04:14.943309Z",
                            "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                            "name": "test_name"
                        }
                    ],
                    "text": "test_text",
                    "url": "www.some.url",
                }
            ],
            "total": 1
        }

News Detail
-----------

.. http:get:: /news/management/news/(uuid:pk)

    Fetches news details.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json string assigned_crew_member: assigned crew member email
    :>json string comment: news comment
    :>json string current_verdict: news current verdict
    :>json boolean deleted: is news deleted
    :>json list domains: list of domains
    :>json object expert_opinion: expert opinion
    :>json list fact_checker_opinions: list of fact checker opinions
    :>json uuid id: news id
    :>json boolean is_duplicate: is news duplicated
    :>json boolean is_pinned: is news pinned
    :>json boolean is_published: is news published
    :>json boolean is_sensitive: is news sensitive
    :>json string origin: news origin
    :>json datetime reported_at: news reported at
    :>json list sensitive_keywords: list of sensitive keywords
    :>json string screenshot_url: news url
    :>json list tags: list of tags
    :>json string text: news text
    :>json string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        GET /news/management/news/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, OPTIONS
        Content-Type: application/json

        {
            "assigned_crew_member": "test@crew.com",
            "comment": "test_comment",
            "current_verdict": "no_verdict",
            "deleted": false,
            "domains": [
                {
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                    "name": "test_name"
                }
            ],
            "expert_opinion": null,
            "fact_checker_opinions": [],
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "is_duplicate": false,
            "is_pinned": true,
            "is_published": true,
            "is_sensitive": true,
            "origin": "plugin",
            "reported_at": "2020-06-05T11:27:11.886109Z",
            "screenshot_url": "www.some_screenshot.url",
            "sensitive_keywords": [
                "sensitive_keyword"
            ],
            "tags": [
                {
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                    "name": "test_name"
                }
            ],
            "text": "test_text",
            "url": "www.some.url",
        }

News Update
-----------

.. http:patch:: /news/management/news/(uuid:pk)

    Updates news.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string comment: news comment
    :<json boolean deleted: is news deleted
    :<json list domains: list of domain ids to be associated with news
    :<json boolean is_pinned: is news pinned
    :<json boolean is_published: is news published
    :<json string url: news url
    :<json list tags: list of tags to be associated with news
    :<json string text: news text

    :>json string assigned_crew_member: assigned crew member email
    :>json string comment: news comment
    :>json string current_verdict: news current verdict
    :>json boolean deleted: is news deleted
    :>json list domains: list of domains
    :>json object expert_opinion: expert opinion
    :>json list fact_checker_opinions: list of fact checker opinions
    :>json uuid id: news id
    :>json boolean is_duplicate: is news duplicated
    :>json boolean is_pinned: is news pinned
    :>json boolean is_published: is news published
    :>json boolean is_sensitive: is news sensitive
    :>json string origin: news origin
    :>json datetime reported_at: news reported at
    :>json list sensitive_keywords: list of sensitive keywords
    :>json string screenshot_url: news url
    :>json list tags: list of tags
    :>json string text: news text
    :>json string url: news url

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        PATCH /news/management/news/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "comment": "test_update_comment",
            "deleted": true,
            "domains": ["682bf191-b888-4bba-a480-750efbfcbd53"],
            "is_pinned": true,
            "text": "test_update_text",
            "url": "www.some_updated.url",
            "tags": ["tag_1", "tag2"]
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PATCH, OPTIONS
        Content-Type: application/json

        {
            "assigned_crew_member": "test@crew.com",
            "comment": "test_comment",
            "current_verdict": "no_verdict",
            "deleted": false,
            "domains": [
                {
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                    "name": "test_name"
                }
            ],
            "expert_opinion": null,
            "fact_checker_opinions": [],
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "is_duplicate": false,
            "is_pinned": true,
            "is_published": true,
            "is_sensitive": true,
            "origin": "plugin",
            "reported_at": "2020-06-05T11:27:11.886109Z",
            "screenshot_url": "www.some_screenshot.url",
            "sensitive_keywords": [
                "sensitive_keyword"
            ],
            "tags": [
                {
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                    "name": "test_name"
                }
            ],
            "text": "test_text",
            "url": "www.some.url",
        }

News Add Screenshot
-------------------

.. http:patch:: /news/management/news-image/(uuid:pk)

    Updates news with given screenshot.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<multipart bytes image: image file

    :statuscode 204: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist
    :statuscode 503: storage service unavailable

    **Allowed for user roles:**

    ``admin``
    ``moderator``

Expert Opinion Update
---------------------

.. http:put:: /news/management/expert-opinion/(int:pk)

    Updates expert opinion.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string comment: comment (required for type ``verdict``)
    :<json string confirmation_sources: confirmation sources (required for type ``verdict``)
    :<json string duplicate_reference: news duplicate reference (required for type ``duplicate``)
    :<json string title: title (required for type ``verdict``)
    :<json string type: opinion type from values ``verdict, spam, duplicate`` (required)
    :<json string verdict: verdict from values ``true, false, unidentified`` (required for type ``verdict``)

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

    **Allowed for user roles:**

    ``admin``
    ``moderator``
    ``expert``
    ``specialist``

    **Example request**:

    .. http:example:: curl httpie

        PUT /news/management/expert-opinion/1 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "comment": "Thinking through all the facts and other dependencies, yes.",
            "confirmation_sources": "drop.com",
            "duplicate_reference": null,
            "title": "Some random title",
            "type": "verdict",
            "verdict": "true"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: PUT, OPTIONS
        Content-Type: application/json

        {
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
            "verdict": "true"
        }

Fact Checker Opinion Update
---------------------------

.. http:put:: /news/management/fact-checker-opinion/(int:pk)

    Updates fact checker opinion.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json string comment: comment (required for type ``verdict``)
    :<json string confirmation_sources: confirmation sources (required for type ``verdict``)
    :<json string duplicate_reference: news duplicate reference (required for type ``duplicate``)
    :<json string title: title (required for type ``verdict``)
    :<json string type: opinion type from values ``verdict, spam, duplicate`` (required)
    :<json string verdict: verdict from values ``true, false, unidentified`` (required for type ``verdict``)

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

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        PUT /news/management/fact-checker-opinion/1 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "comment": "Thinking through all the facts and other dependencies, yes.",
            "confirmation_sources": "drop.com",
            "duplicate_reference": null,
            "title": "Some random title",
            "type": "verdict",
            "verdict": "true"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: PUT, OPTIONS
        Content-Type: application/json

        {
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
            "verdict": "true"
        }

News Assign To Expert/Specialist
--------------------------------

.. http:patch:: /news/management/news/(uuid:pk)/assign

    Assign news to a certain expert/specialist. Replaces assignee in case another user is
    already assigned to given news.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json uuid assignee: pk of user the news to be assigned to
    :<json boolean replace_assignee: indicates whether assignee should be replaced

    :statuscode 204: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``admin``
    ``moderator``

    **Example request**:

    .. http:example:: curl httpie

        PATCH /news/management/news/52bccefb-b122-4fe8-aab2-cf6061da20a7/assign HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
            "assignee": "aaabf191-b888-4bba-a480-750efbfcbd53",
            "replace_assignee": true
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Allow: PATCH, OPTIONS
        Content-Type: application/json


News Dismiss From Expert/Specialist
-----------------------------------

.. http:delete:: /news/management/news/(uuid:pk)/dismiss-assignment

    Removes news assignment from specialist or expert.

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

        PATCH /news/management/news/52bccefb-b122-4fe8-aab2-cf6061da20a7/dismiss-assignment HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Allow: DELETE, OPTIONS
        Content-Type: application/json