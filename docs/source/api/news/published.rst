Published
=========

Endpoints related to news available publicly.

News List
---------

.. http:get:: news/published/news

    Fetches list of published news.

    :query boolean is_pinned: filtering pinned items
    :query list tags[]: filtering by a list of tag names (conjunction)
    :query list domains[]: filtering by a list of domain names (alternative)

    :>jsonarr datetime date: news created at
    :>jsonarr list domains: domains associated with news
    :>jsonarr object expert_opinion: expert opinion for news
    :>jsonarr list fact_checker_opinions: list of fact checker opinions
    :>jsonarr uuid id: news id
    :>jsonarr boolean is_pinned: is news pinned
    :>jsonarr datetime reported_at: news reported at
    :>jsonarr string screenshot_url: screenshot url
    :>jsonarr list tags: list of tag objects associated with news
    :>jsonarr string text: news text
    :>jsonarr string title: news title
    :>jsonarr string url: news url
    :>jsonarr string verdict: news verdict
    :>jsonarr boolean verified_by_expert: is news verified by expert

    :statuscode 200: success

    **Example request**:

    .. http:example:: curl httpie

        GET /news/published/news HTTP/1.1
        Content-Type: application/json

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
                    "date": "2020-05-25T08:01:05.849857Z",
                    "domains": [
                        {
                            "created_at": "2020-06-02T06:46:52.989155Z",
                            "id": "8f738572-2242-46ff-9274-182855718f50",
                            "name": "abc"
                        }
                    ],
                    "expert_opinion": {
                        "comment": "comment",
                        "confirmation_sources": "sources",
                        "date": "2020-06-02T07:05:24.087310Z",
                        "title": "title",
                        "verdict": "true"
                    },
                    "fact_checker_opinions": [
                        {
                            "comment": "comment",
                            "confirmation_sources": "sources",
                            "date": "2020-06-02T07:05:24.087310Z",
                            "title": "title",
                            "verdict": "true"
                        }
                    ],
                    "id": "f32d2d9c-000a-4c22-87cb-451652351609",
                    "is_pinned": false,
                    "reported_at": "2020-05-25T07:12:12.365971Z",
                    "screenshot_url": "https://test.com/test.jpg",
                    "tags": [
                        {
                            "created_at": "2020-06-02T06:46:52.989155Z",
                            "id": "8f738572-2242-46ff-9274-182855718f50",
                            "name": "abc"
                        }
                    ],
                    "text": "text",
                    "title": "title",
                    "url": "https://test.com",
                    "verdict": "true",
                    "verified_by_expert": true
                }
            ],
            "total": 1
        }

News Detail
-----------

.. http:get:: news/published/news/(uuid:pk)

    Fetches details of published news.

    :>json datetime date: news created at
    :>json list domains: domains associated with news
    :>json object expert_opinion: expert opinion for news
    :>json list fact_checker_opinions: list of fact checker opinions
    :>json uuid id: news id
    :>json boolean is_pinned: is news pinned
    :>json datetime reported_at: news reported at
    :>json string screenshot_url: screenshot url
    :>json list tags: list of tag objects associated with news
    :>json string text: news text
    :>json string title: news title
    :>json string url: news url
    :>json string verdict: news verdict
    :>json boolean verified_by_expert: is news verified by expert

    :statuscode 200: success
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        GET /news/published/news/f32d2d9c-000a-4c22-87cb-451652351609 HTTP/1.1
        Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "date": "2020-05-25T08:01:05.849857Z",
            "domains": [
                {
                    "created_at": "2020-06-02T06:46:52.989155Z",
                    "id": "8f738572-2242-46ff-9274-182855718f50",
                    "name": "abc"
                }
            ],
            "expert_opinion": {
                "comment": "comment",
                "confirmation_sources": "sources",
                "date": "2020-06-02T07:05:24.087310Z",
                "title": "title",
                "verdict": "true"
            },
            "fact_checker_opinions": [
                {
                    "comment": "comment",
                    "confirmation_sources": "sources",
                    "date": "2020-06-02T07:05:24.087310Z",
                    "title": "title",
                    "verdict": "true"
                }
            ],
            "id": "f32d2d9c-000a-4c22-87cb-451652351609",
            "is_pinned": false,
            "reported_at": "2020-05-25T07:12:12.365971Z",
            "screenshot_url": "https://test.com/test.jpg",
            "tags": [
                {
                    "created_at": "2020-06-02T06:46:52.989155Z",
                    "id": "8f738572-2242-46ff-9274-182855718f50",
                    "name": "abc"
                }
            ],
            "text": "text",
            "title": "title",
            "url": "https://test.com",
            "verdict": "true",
            "verified_by_expert": true
        }
