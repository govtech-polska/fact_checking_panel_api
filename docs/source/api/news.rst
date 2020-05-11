News
====

Endpoints related to news management.

Expert News List
----------------

.. http:get:: /api/expert/news

    Fetches news for experts.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>jsonarr string comment: news comment
    :>jsonarr string current_verdict: news current verdict
    :>jsonarr object expert_opinion: expert opinion object
    :>jsonarr list factcheckeropinion_set: list of fact checker opinion objects
    :>jsonarr uuid id: news id
    :>jsonarr boolean is_about_corona_virus: is news about corona virus
    :>jsonarr boolean is_duplicate: is news duplicated
    :>jsonarr boolean is_sensitive: is news sensitive
    :>jsonarr boolean is_spam: is news considered spam
    :>jsonarr list newssensitivekeyword_set: list of sensitive keywords
    :>jsonarr datetime reported_at: news reported at
    :>jsonarr string screenshot_url: news screenshot url
    :>jsonarr string text: news text
    :>jsonarr string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Example request**:

    .. http:example:: curl httpie

        GET /api/expert/news HTTP/1.1
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
                    "current_verdict": true,
                    "expert_opinion": {},
                    "factcheckeropinion_set": [],
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "is_about_corona_virus": true,
                    "is_duplicate": false,
                    "is_sensitive": false
                    "is_spam": false,
                    "newssensitivekeyword_set": [],
                    "reported_at": "2020-05-11T05:04:14.943309Z",
                    "screenshot_url": "www.screenshot.url"
                    "test": "test_text",
                    "url": "www.test.url"
                }
            ],
            "total": 1
        }

Expert News Detail
------------------

.. http:get:: /api/expert/news/(uuid:pk)

    Fetches news details for experts.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json string comment: news comment
    :>json string current_verdict: news current verdict
    :>json object expert_opinion: expert opinion object
    :>json list factcheckeropinion_set: list of fact checker opinion objects
    :>json uuid id: news id
    :>json boolean is_about_corona_virus: is news about corona virus
    :>json boolean is_duplicate: is news duplicated
    :>json boolean is_sensitive: is news sensitive
    :>json boolean is_spam: is news considered spam
    :>json list newssensitivekeyword_set: list of sensitive keywords
    :>json datetime reported_at: news reported at
    :>json string screenshot_url: news screenshot url
    :>json string text: news text
    :>json string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        GET /api/expert/news/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "comment": "test_comment",
            "current_verdict": true,
            "expert_opinion": {},
            "factcheckeropinion_set": [],
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "is_about_corona_virus": true,
            "is_duplicate": false,
            "is_sensitive": false
            "is_spam": false,
            "newssensitivekeyword_set": [],
            "reported_at": "2020-05-11T05:04:14.943309Z",
            "screenshot_url": "www.screenshot.url"
            "test": "test_text",
            "url": "www.test.url"
        }


Expert Create Opinion For News
------------------------------

.. http:post:: /api/expert/news/(uuid:pk)/create_opinion

    Creates expert opinion for given news.

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
    :>json boolean is_duplicate: is new duplicated
    :>json string title: title
    :>json string verdict: verdict

    :statuscode 201: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        POST /api/expert/news/52bccefb-b122-4fe8-aab2-cf6061da20a7/create_opinion HTTP/1.1
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
        Allow: POST, OPTIONS
        Content-Type: application/json

        {
            "about_corona_virus": true,
            "comment": "Thinking through all the facts and other dependencies, yes.",
            "confirmation_sources": "drop.com",
            "duplicate_reference": null,
            "is_duplicate": false,
            "title": "Some random title",
            "verdict": true
        }

Fact Checker News List
----------------------

.. http:get:: /api/fact_checker/news

    Fetches news for fact checkers.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>jsonarr string comment: news comment
    :>jsonarr string current_verdict: news current verdict
    :>jsonarr object expert_opinion: expert opinion object
    :>jsonarr list factcheckeropinion_set: list of fact checker opinion objects
    :>jsonarr uuid id: news id
    :>jsonarr boolean is_about_corona_virus: is news about corona virus
    :>jsonarr boolean is_duplicate: is news duplicated
    :>jsonarr boolean is_sensitive: is news sensitive
    :>jsonarr boolean is_spam: is news considered spam
    :>jsonarr list newssensitivekeyword_set: list of sensitive keywords
    :>jsonarr datetime reported_at: news reported at
    :>jsonarr string screenshot_url: news screenshot url
    :>jsonarr string text: news text
    :>jsonarr string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Example request**:

    .. http:example:: curl httpie

        GET /api/fact_checker/news HTTP/1.1
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
                    "current_verdict": true,
                    "expert_opinion": {},
                    "factcheckeropinion_set": [],
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "is_about_corona_virus": true,
                    "is_duplicate": false,
                    "is_sensitive": false
                    "is_spam": false,
                    "newssensitivekeyword_set": [],
                    "reported_at": "2020-05-11T05:04:14.943309Z",
                    "screenshot_url": "www.screenshot.url"
                    "test": "test_text",
                    "url": "www.test.url"
                }
            ],
            "total": 1
        }

Fact Checker News Detail
------------------------

.. http:get:: /api/fact_checker/news/(uuid:pk)

    Fetches news details for fact checkers.

    :reqheader Authorization: token in format ``Token <token_value>``

    :>json string comment: news comment
    :>json string current_verdict: news current verdict
    :>json object expert_opinion: expert opinion object
    :>json list factcheckeropinion_set: list of fact checker opinion objects
    :>json uuid id: news id
    :>json boolean is_about_corona_virus: is news about corona virus
    :>json boolean is_duplicate: is news duplicated
    :>json boolean is_sensitive: is news sensitive
    :>json boolean is_spam: is news considered spam
    :>json list newssensitivekeyword_set: list of sensitive keywords
    :>json datetime reported_at: news reported at
    :>json string screenshot_url: news screenshot url
    :>json string text: news text
    :>json string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        GET /api/fact_checker/news/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "comment": "test_comment",
            "current_verdict": true,
            "expert_opinion": {},
            "factcheckeropinion_set": [],
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "is_about_corona_virus": true,
            "is_duplicate": false,
            "is_sensitive": false
            "is_spam": false,
            "newssensitivekeyword_set": [],
            "reported_at": "2020-05-11T05:04:14.943309Z",
            "screenshot_url": "www.screenshot.url"
            "test": "test_text",
            "url": "www.test.url"
        }


Fact Checker Create Opinion For News
------------------------------------

.. http:post:: /api/fact_checker/news/(uuid:pk)/create_opinion

    Creates fact checker opinion for given news.

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
    :>json boolean is_duplicate: is new duplicated
    :>json string title: title
    :>json string verdict: verdict

    :statuscode 201: success
    :statuscode 400: invalid payload
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        POST /api/fact_checker/news/52bccefb-b122-4fe8-aab2-cf6061da20a7/create_opinion HTTP/1.1
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
        Allow: POST, OPTIONS
        Content-Type: application/json

        {
            "about_corona_virus": true,
            "comment": "Thinking through all the facts and other dependencies, yes.",
            "confirmation_sources": "drop.com",
            "duplicate_reference": null,
            "is_duplicate": false,
            "title": "Some random title",
            "verdict": true
        }

News Verified List
------------------

.. http:get:: /api/news_verified

    Fetches list of verified news.

    :>jsonarr string comment: news comment
    :>jsonarr string current_verdict: news current verdict
    :>jsonarr object expertopinion: expert opinion object
    :>jsonarr list factcheckeropinion_set: list of fact checker opinion objects
    :>jsonarr uuid id: news id
    :>jsonarr boolean is_about_corona_virus: is news about corona virus
    :>jsonarr boolean is_assigned_to_me: is news assigned to requesting user
    :>jsonarr boolean is_duplicate: is news duplicated
    :>jsonarr datetime reported_at: news reported at
    :>jsonarr string screenshot_url: news screenshot url
    :>jsonarr string text: news text
    :>jsonarr string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions

    **Example request**:

    .. http:example:: curl httpie

        GET /api/news_verified HTTP/1.1
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
                    "current_verdict": true,
                    "expertopinion": {},
                    "factcheckeropinion_set": [],
                    "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
                    "is_about_corona_virus": true,
                    "is_assigned_to_me": true,
                    "is_duplicate": false,
                    "reported_at": "2020-05-11T05:04:14.943309Z",
                    "screenshot_url": "www.screenshot.url"
                    "test": "test_text",
                    "url": "www.test.url"
                }
            ],
            "total": 1
        }

News Verified Detail
--------------------

.. http:get:: /api/news_verified/(uuid:pk)

    Fetches list of verified news.

    :>json string comment: news comment
    :>json string current_verdict: news current verdict
    :>json object expertopinion: expert opinion object
    :>json list factcheckeropinion_set: list of fact checker opinion objects
    :>json uuid id: news id
    :>json boolean is_about_corona_virus: is news about corona virus
    :>json boolean is_assigned_to_me: is news assigned to requesting user
    :>json boolean is_duplicate: is news duplicated
    :>json datetime reported_at: news reported at
    :>json string screenshot_url: news screenshot url
    :>json string text: news text
    :>json string url: news url

    :statuscode 200: success
    :statuscode 401: not authorized
    :statuscode 403: invalid permissions
    :statuscode 404: does not exist

    **Example request**:

    .. http:example:: curl httpie

        GET /api/news_verified/52bccefb-b122-4fe8-aab2-cf6061da20a7 HTTP/1.1
        Content-Type: application/json
        Authorization: Token decdb3eb3e17ea10753de3eedf73252b9f0dcdb326cf78e78d07ab2c97cd0651

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json

        {
            "comment": "test_comment",
            "current_verdict": true,
            "expertopinion": {},
            "factcheckeropinion_set": [],
            "id": "52bccefb-b122-4fe8-aab2-cf6061da20a7",
            "is_about_corona_virus": true,
            "is_assigned_to_me": true,
            "is_duplicate": false,
            "reported_at": "2020-05-11T05:04:14.943309Z",
            "screenshot_url": "www.screenshot.url"
            "test": "test_text",
            "url": "www.test.url"
        }
