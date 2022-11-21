fqdn                = "panel-api.fakehunter.pap.pl"
domain              = "fakehunter.pap.pl"
environment         = "prod"
vpc_id              = "vpc-0e937b59f01e9c889"
azs                 = ["eu-central-1a", "eu-central-1b", "eu-central-1c"]
public_subnets      = ["subnet-09fc5906f7bc6994b", "subnet-01a4696859a224d2a", "subnet-0900caf0ab41e57e7"]
private_subnets     = ["subnet-03bb0e34107109be1", "subnet-01c4b4aae03bd634d", "subnet-02c9d780ef6b313bd"]
certificate_arn     = "arn:aws:acm:eu-central-1:433731253015:certificate/52135fa4-83ac-4ede-b098-5c1739d4707f"
postgres_host       = "fhprod.cluster-ce3brpofwmro.eu-central-1.rds.amazonaws.com"
postgres_username   = "master"
name                = "fakehunter"
bucket              = "fakehunter-prod-tfstate"
acl                 = "private"
key                 = "sfnf-panel"
infra_statefile_key = "fakehunter-prod"
region              = "eu-central-1"
encrypt             = "true"
dynamodb_table      = "fakehunter-prod-tfstate"
ecr_registry        = "433731253015.dkr.ecr.eu-central-1.amazonaws.com/sfnf-panel-prod"
ecr_registry_st     = "433731253015.dkr.ecr.eu-central-1.amazonaws.com/sfnf-panel-scheduler-prod"
cors_allow_all      = "True"
debug               = "False"
schedule_expr       = "cron(0 7-22 * * ? *)"
chatbot_api_url     = "https://30pq6qpfn9.execute-api.eu-central-1.amazonaws.com/prod/v1"
chatbot_api_key     = "aTF6uNUs4i3FIVVNpied24EUcOskyMRI6pBvrM7G"
images_bucket       = "sfnf-collector-prod"
