from envparse import env

EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="sfnf@dook.pro")

ANYMAIL = {
    "AMAZON_SES_CLIENT_PARAMS": {
        # example: override normal Boto credentials specifically for Anymail
        "aws_access_key_id": env("AWS_ACCESS_KEY_ID", default=""),
        "aws_secret_access_key": env("AWS_SECRET_ACCESS_KEY", default=""),
        "region_name": env("REGION_NAME", default=""),
        # override other default options
        "config": {"connect_timeout": 30, "read_timeout": 30,},
    },
}
