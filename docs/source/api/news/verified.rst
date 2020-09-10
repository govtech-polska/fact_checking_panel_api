Verified
========

Endpoints related to verified news.


News List
---------

.. http:get:: /news/verified/news

    Fetches list of verified news.

    :query string current_verdict: filtering by verdict from ``true, false, spam, unidentified, no_verdict, dispute``
    :query list domains[]: filtering by a list of domain names
    :query boolean is_assigned_to_me: filtering duplicate items
    :query boolean is_duplicate: filtering duplicate items
    :query boolean is_published: filtering for published news
    :query string search: search filter (by ``text`` field)
    :query string origin: filtering by news origin from ``plugin, chatbot, mobile``
    :query list tags[]: filtering by a list of tag names

    :>jsonarr string comment: news comment
    :>jsonarr string current_verdict: news current verdict
    :>jsonarr object expert_opinion: expert opinion object
    :>jsonarr list fact_checker_opinions: list of fact checker opinion objects
    :>jsonarr uuid id: news id
    :>jsonarr boolean is_assigned_to_me: is news assigned to requesting user
    :>jsonarr boolean is_duplicate: is news duplicated
    :>jsonarr boolean is_published: is news published
    :>jsonarr string origin: news origin
    :>jsonarr datetime reported_at: news reported at
    :>jsonarr string screenshot_url: news screenshot url
    :>jsonarr list sensitive_keywords: list of sensitive keywords
    :>jsonarr list tags: list of tags
    :>jsonarr string text: news text
    :>jsonarr string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Example request**:

    .. http:example:: curl httpie

        GET /news/verified/news HTTP/1.1
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
                    "expert_opinion": {},
                    "fact_checker_opinions": [],
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "is_assigned_to_me": true,
                    "is_duplicate": false,
                    "is_published": true,
                    "origin": "plugin",
                    "reported_at": "2020-05-11T05:04:14.943309Z",
                    "screenshot_url": "www.screenshot.url",
                    "sensitive_keywords": [],
                    "tags": [
                        {
                            "created_at": "2020-05-11T05:04:14.943309Z",
                            "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                            "name": "test_name"
                        }
                    ],
                    "test": "test_text",
                    "url": "www.test.url"
                }
            ],
            "total": 1
        }

News Detail
-----------

.. http:get:: /news/verified/news/(uuid:pk)

    Fetches verified news details.

    :>json string comment: news comment
    :>json string current_verdict: news current verdict
    :>json object expert_opinion: expert opinion object
    :>json list fact_checker_opinions: list of fact checker opinion objects
    :>json uuid id: news id
    :>json boolean is_assigned_to_me: is news assigned to requesting user
    :>json boolean is_duplicate: is news duplicated
    :>json boolean is_published: is news published
    :>json string origin: news origin
    :>json datetime reported_at: news reported at
    :>json string screenshot_url: news screenshot url
    :>json list sensitive_keywords: list of sensitive keywords
    :>json list tags: list of tags
    :>json string text: news text
    :>json string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        GET /news/verified/news/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
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
            "expert_opinion": {},
            "fact_checker_opinions": [],
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "is_assigned_to_me": true,
            "is_duplicate": false,
            "is_published": true,
            "origin": "plugin",
            "reported_at": "2020-05-11T05:04:14.943309Z",
            "screenshot_url": "www.screenshot.url",
            "sensitive_keywords": [],
            "tags": [
                {
                    "created_at": "2020-05-11T05:04:14.943309Z",
                    "id": "52bcce12-b122-4fe8-aab2-cf6061da20a7",
                    "name": "test_name"
                }
            ],
            "test": "test_text",
            "url": "www.test.url"
        }
