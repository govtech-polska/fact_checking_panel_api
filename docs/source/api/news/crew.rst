Crew
====

Endpoints related to crew management for news.

Expert News List
----------------

.. http:get:: /news/crew/expert/news

    Fetches news for experts.

    :reqheader Authorization: token in format ``Token <token_value>``

    :query boolean assigned_to_me: filtering for news assigned to requesting user
    :query string current_verdict: filtering by verdict from ``true, false, spam, unidentified, no_verdict, dispute``
    :query list domains[]: filtering by a list of domain names
    :query boolean is_duplicate: filtering by duplicates
    :query boolean is_sensitive: filtering for news with sensitive keywords
    :query boolean is_spam: filtering by spam
    :query boolean is_verified: filtering for verified news
    :query string origin: filtering by news origin from ``plugin, chatbot, mobile``
    :query string search: search filter (by ``text`` field)
    :query list tags[]: filtering by a list of tag names

    :>jsonarr string assigned_crew_member: assigned crew member email
    :>jsonarr string comment: news comment
    :>jsonarr string current_verdict: news current verdict
    :>jsonarr object expert_opinion: expert opinion object
    :>jsonarr list fact_checker_opinions: list of fact checker opinion objects
    :>jsonarr uuid id: news id
    :>jsonarr boolean is_duplicate: is news duplicated
    :>jsonarr boolean is_published: is news published
    :>jsonarr boolean is_sensitive: is news sensitive
    :>jsonarr boolean is_spam: is news considered spam
    :>jsonarr string origin: news origin
    :>jsonarr datetime reported_at: news reported at
    :>jsonarr list sensitive_keywords: list of sensitive keywords
    :>jsonarr string screenshot_url: news screenshot url
    :>jsonarr list tags: list of tags
    :>jsonarr string text: news text
    :>jsonarr string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Allowed for user roles:**

    ``expert``
    ``specialist``

    **Example request**:

    .. http:example:: curl httpie

        GET /news/crew/expert/news HTTP/1.1
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
                    "current_verdict": "true",
                    "expert_opinion": {},
                    "fact_checker_opinions": [],
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "is_duplicate": false,
                    "is_published": false,
                    "is_sensitive": false,
                    "is_spam": false,
                    "origin": "plugin",
                    "reported_at": "2020-05-11T05:04:14.943309Z",
                    "sensitive_keywords": [],
                    "screenshot_url": "www.screenshot.url",
                    "tags": [
                        {
                            "created_at": "2020-05-11T05:04:14.943309Z",
                            "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                            "name": "test_name"
                        }
                    ],
                    "text": "test_text",
                    "url": "www.test.url"
                }
            ],
            "total": 1
        }

Expert News Detail
------------------

.. http:get:: /news/crew/expert/news/(uuid:pk)

    Fetches news details for experts.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json string assigned_crew_member: assigned crew member email
    :>json string comment: news comment
    :>json string current_verdict: news current verdict
    :>json object expert_opinion: expert opinion object
    :>json list fact_checker_opinions: list of fact checker opinion objects
    :>json uuid id: news id
    :>json boolean is_duplicate: is news duplicated
    :>json boolean is_published: is news published
    :>json boolean is_sensitive: is news sensitive
    :>json boolean is_spam: is news considered spam
    :>json string origin: news origin
    :>json datetime reported_at: news reported at
    :>json list sensitive_keywords: list of sensitive keywords
    :>json string screenshot_url: news screenshot url
    :>json list tags: list of tags
    :>json string text: news text
    :>json string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``expert``
    ``specialist``

    **Example request**:

    .. http:example:: curl httpie

        GET /news/crew/expert/news/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "assigned_crew_member": "test@crew.com",
            "comment": "test_comment",
            "current_verdict": "true",
            "expert_opinion": {},
            "fact_checker_opinions": [],
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "is_duplicate": false,
            "is_published": false,
            "is_sensitive": false,
            "is_spam": false,
            "origin": "plugin",
            "reported_at": "2020-05-11T05:04:14.943309Z",
            "sensitive_keywords": [],
            "screenshot_url": "www.screenshot.url",
            "tags": [
                {
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                    "name": "test_name"
                }
            ],
            "text": "test_text",
            "url": "www.test.url"
        }


Expert Create Opinion For News
------------------------------

.. http:post:: /news/crew/expert/news/(uuid:pk)/create-opinion

    Creates expert opinion for given news.

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
    :>json boolean is_duplicate: is new duplicated
    :>json string title: title
    :>json string verdict: verdict

    :statuscode 201: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``moderator``
    ``expert``
    ``specialist``

    **Example request**:

    .. http:example:: curl httpie

        POST /news/crew/expert/news/52bccefb-b122-4fe8-aab2-cf6061da20a7/create-opinion HTTP/1.1
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
        Allow: POST, OPTIONS
        Content-Type: application/json

        {
            "comment": "Thinking through all the facts and other dependencies, yes.",
            "confirmation_sources": "drop.com",
            "duplicate_reference": null,
            "id": 1,
            "is_duplicate": false,
            "title": "Some random title",
            "verdict": "true"
        }


Expert Assign List Of Tags For News
-----------------------------------

.. http:post:: /news/crew/expert/news/(uuid:pk)/assign-tags

    Assigns tags for given news.

    :reqheader Authorization: token in format ``Token <token_value>``

    :<json list tags: list of tag names

    :>json string assigned_crew_member: assigned crew member email
    :>json string comment: news comment
    :>json string current_verdict: news current verdict
    :>json object expert_opinion: expert opinion object
    :>json list fact_checker_opinions: list of fact checker opinion objects
    :>json uuid id: news id
    :>json boolean is_duplicate: is news duplicated
    :>json boolean is_published: is news published
    :>json boolean is_sensitive: is news sensitive
    :>json boolean is_spam: is news considered spam
    :>json string origin: news origin
    :>json datetime reported_at: news reported at
    :>json list sensitive_keywords: list of sensitive keywords
    :>json string screenshot_url: news screenshot url
    :>json list tags: list of tags
    :>json string text: news text
    :>json string url: news url

    :statuscode 200: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``expert``
    ``specialist``

    **Example request**:

    .. http:example:: curl httpie

        POST /news/crew/expert/news/52bccefb-b122-4fe8-aab2-cf6061da20a7/assign-tags HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

        {
           "tags": ["tag_1", "tag_2"]
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "assigned_crew_member": "test@crew.com",
            "comment": "test_comment",
            "current_verdict": "true",
            "expert_opinion": {},
            "fact_checker_opinions": [],
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "is_duplicate": false,
            "is_published": false,
            "is_sensitive": false,
            "is_spam": false,
            "origin": "plugin",
            "reported_at": "2020-05-11T05:04:14.943309Z",
            "sensitive_keywords": [],
            "screenshot_url": "www.screenshot.url",
            "tags": [
                {
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                    "name": "tag_1"
                },
                {
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "id": "qqqcce12-b122-4fe8-aab2-cf6061da20a7",
                    "name": "tag_2"
                }
            ],
            "text": "test_text",
            "url": "www.test.url"
        }

Expert Dismiss Assignment To News
---------------------------------

.. http:patch:: /news/crew/expert/news/(uuid:pk)/dismiss-assignment

    Rejects news verification, previously assigned to requesting user.

    :reqheader Authorization: token in format ``Token <token_value>``

    :statuscode 204: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``expert``
    ``specialist``

    **Example request**:

    .. http:example:: curl httpie

        PATCH /news/crew/expert/news/52bccefb-b122-4fe8-aab2-cf6061da20a7/dismiss-assignment HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Allow: PATCH, OPTIONS
        Content-Type: application/json


Fact Checker News List
----------------------

.. http:get:: /news/crew/fact-checker/news

    Fetches news for fact checkers.

    :reqheader Authorization: token in format ``Token <token_value>``

    :query string search: search filter (by ``text`` field)
    :query list tags[]: filtering by a list of tag names
    :query boolean is_opined: listing news containing requesting user opinion

    :>jsonarr string comment: news comment
    :>jsonarr string current_verdict: news current verdict
    :>jsonarr uuid id: news id
    :>jsonarr boolean is_duplicate: is news duplicated
    :>jsonarr boolean is_sensitive: is news sensitive
    :>jsonarr boolean is_spam: is news considered spam
    :>jsonarr string origin: news origin
    :>jsonarr datetime reported_at: news reported at
    :>jsonarr string screenshot_url: news screenshot url
    :>jsonarr list tags: list of tags
    :>jsonarr string text: news text
    :>jsonarr string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Allowed for user roles:**

    ``fact_checker``

    **Example request**:

    .. http:example:: curl httpie

        GET /news/crew/fact-checker/news HTTP/1.1
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
                    "comment": "test_comment",
                    "current_verdict": "true",
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "is_duplicate": false,
                    "is_sensitive": false,
                    "is_spam": false,
                    "origin": "plugin",
                    "reported_at": "2020-05-11T05:04:14.943309Z",
                    "screenshot_url": "www.screenshot.url",
                    "tags": [
                        {
                            "created_at": "2020-05-11T05:04:14.943309Z",
                            "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                            "name": "test_name"
                        }
                    ],
                    "text": "test_text",
                    "url": "www.test.url"
                }
            ],
            "total": 1
        }

Fact Checker News Detail
------------------------

.. http:get:: /news/crew/fact-checker/news/(uuid:pk)

    Fetches news details for fact checkers.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json string comment: news comment
    :>json string current_verdict: news current verdict
    :>json uuid id: news id
    :>json boolean is_duplicate: is news duplicated
    :>json boolean is_sensitive: is news sensitive
    :>json boolean is_spam: is news considered spam
    :>json string origin: news origin
    :>json datetime reported_at: news reported at
    :>json string screenshot_url: news screenshot url
    :>json list tags: list of tags
    :>json string text: news text
    :>json string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``fact_checker``

    **Example request**:

    .. http:example:: curl httpie

        GET /news/crew/fact-checker/news/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "comment": "test_comment",
            "current_verdict": "true",
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "is_duplicate": false,
            "is_sensitive": false,
            "is_spam": false,
            "origin": "plugin",
            "reported_at": "2020-05-11T05:04:14.943309Z",
            "screenshot_url": "www.screenshot.url",
            "tags": [
                {
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                    "name": "test_name"
                }
            ],
            "text": "test_text",
            "url": "www.test.url"
        }


Fact Checker Create Opinion For News
------------------------------------

.. http:post:: /news/crew/fact-checker/news/(uuid:pk)/create-opinion

    Creates fact checker opinion for given news.

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
    :>json boolean is_duplicate: is new duplicated
    :>json string title: title
    :>json string verdict: verdict

    :statuscode 201: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Allowed for user roles:**

    ``fact_checker``

    **Example request**:

    .. http:example:: curl httpie

        POST /news/crew/fact-checker/news/52bccefb-b122-4fe8-aab2-cf6061da20a7/create-opinion HTTP/1.1
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
        Allow: POST, OPTIONS
        Content-Type: application/json

        {
            "comment": "Thinking through all the facts and other dependencies, yes.",
            "confirmation_sources": "drop.com",
            "duplicate_reference": null,
            "id": 1,
            "is_duplicate": false,
            "title": "Some random title",
            "verdict": "true"
        }