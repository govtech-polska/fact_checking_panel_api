provider "aws" {
  region = "eu-central-1"
}

terraform {
  backend "s3" {
  }
}

data "aws_route53_zone" "selected" {
  name = "${var.domain}"
}

data "terraform_remote_state" "infra" {
  backend = "s3"

  config = {
    bucket = var.bucket
    key    = var.infra_statefile_key
    region = var.region
  }
}

resource "aws_iam_user" "panel" {
  name = "sfnf-panel-${var.environment}-s3"
  path = "/system/"
}

resource "aws_iam_access_key" "panel" {
  user = aws_iam_user.panel.name
}

resource "aws_iam_user_policy" "panel" {
  name   = "sfnf-panel-${var.environment}-ses"
  user   = aws_iam_user.panel.name
  policy = data.aws_iam_policy_document.panel.json
}


data "aws_iam_policy_document" "panel" {
  statement {
    actions = [
      "s3:*"
    ]
    resources = [
      "arn:aws:s3:::sfnf-collector-${var.environment}",
      "arn:aws:s3:::sfnf-collector-${var.environment}/*",
    ]
  }
  statement {
    actions = [
      "ses:*"
    ]
    resources = [
      "*",
    ]
  }
}

module "service" {
  source                       = "git@github.com:dook/sfnf-infra.git//modules/terraform-aws-fargate"
  name_preffix                 = "${var.environment}-sfnf-panel"
  region                       = "eu-central-1"
  vpc_id                       = var.vpc_id
  availability_zones           = [var.azs]
  public_subnets_ids           = var.public_subnets
  private_subnets_ids          = var.private_subnets
  access_cidr_list             = ["0.0.0.0/0"]
  port_lb_external             = "443"
  container_name               = "sfnf-panel-${var.environment}"
  container_image              = "${var.ecr_registry}:${var.image_tag}"
  container_cpu                = 256
  container_memory             = 1024
  container_memory_reservation = 1024
  container_port               = 8000

  internal        = false
  certificate_arn = var.certificate_arn
  create_elb      = false
  elb_sg_id       = data.terraform_remote_state.infra.outputs.elb_sg_id

  environment = [
    {
      name  = "POSTGRES_HOST"
      value = var.postgres_host
    },
    {
      name  = "POSTGRES_READONLY_HOST"
      value = var.postgres_host
    },
    {
      name  = "POSTGRES_USER"
      value = var.postgres_username
    },
    {
      name  = "POSTGRES_DB"
      value = "fh${var.environment}"
    },
    {
      name  = "POSTGRES_PASSWORD"
      value = var.postgres_password
    },
    {
      name  = "CORS_ORIGIN_ALLOW_ALL"
      value = var.cors_allow_all
    },
    {
      name  = "AWS_ACCESS_KEY_ID"
      value = aws_iam_access_key.panel.id
    },
    {
      name  = "AWS_SECRET_ACCESS_KEY"
      value = aws_iam_access_key.panel.secret
    },
    {
      name  = "REGION_NAME"
      value = "eu-central-1"
    },
    {
      name  = "DOMAIN_NAME"
      value = "panel.${var.domain}"
    },
    {
      name  = "EMAIL_HOST_USER"
      value = "noreply@${var.domain}"
    },
    {
      name  = "DEBUG"
      value = var.debug
    },
    {
      name  = "CHATBOT_API_URL"
      value = var.chatbot_api_url
    },
    {
      name  = "CHATBOT_API_KEY"
      value = var.chatbot_api_key
    },
    {
      name  = "BUCKET_NAME"
      value = var.images_bucket
    }
  ]
}

module "scheduled" {
  source                       = "git@github.com:dook/sfnf-infra.git//modules/terraform-aws-fargate-scheduled-task"
  name_preffix                 = "${var.environment}-sfnf-panel-scheduler"
  region                       = "eu-central-1"
  vpc_id                       = var.vpc_id
  availability_zones           = [var.azs]
  public_subnets_ids           = var.public_subnets
  private_subnets_ids          = var.private_subnets
  access_cidr_list             = ["0.0.0.0/0"]
  container_name               = "${var.environment}-scheduled-task"
  container_image              = "${var.ecr_registry_st}:${var.image_tag}"
  container_cpu                = 1024
  container_memory             = 2048
  container_memory_reservation = 2048
  container_port               = 8000
  schedule_expression          = var.schedule_expr
  internal                     = "false"
  environment = [
    {
      name  = "POSTGRES_HOST"
      value = var.postgres_host
    },
    {
      name  = "POSTGRES_READONLY_HOST"
      value = var.postgres_host
    },
    {
      name  = "POSTGRES_USER"
      value = var.postgres_username
    },
    {
      name  = "POSTGRES_DB"
      value = "fh${var.environment}"
    },
    {
      name  = "POSTGRES_PASSWORD"
      value = var.postgres_password
    },
    {
      name  = "AWS_ACCESS_KEY_ID"
      value = aws_iam_access_key.panel.id
    },
    {
      name  = "AWS_SECRET_ACCESS_KEY"
      value = aws_iam_access_key.panel.secret
    },
    {
      name  = "REGION_NAME"
      value = "eu-central-1"
    },
    {
      name  = "CORS_ORIGIN_ALLOW_ALL"
      value = "True"
    },
    {
      name  = "DOMAIN_NAME"
      value = "panel.${var.domain}"
    },
    {
      name  = "EMAIL_HOST_USER"
      value = "noreply@${var.domain}"
    }
  ]
}

resource aws_lb_listener_rule service {
  listener_arn = data.terraform_remote_state.infra.outputs.elb_https_listener_arn

  action {
    type             = "forward"
    target_group_arn = module.service.lb_target_group_arn
  }

  condition {
    host_header {
      values = [var.fqdn]
    }
  }
}

resource "aws_route53_record" "alb_public_web_endpoint" {
  zone_id = data.aws_route53_zone.selected.zone_id
  name    = var.fqdn
  type    = "A"

  alias {
    name                   = data.terraform_remote_state.infra.outputs.elb_dns_name
    zone_id                = data.terraform_remote_state.infra.outputs.elb_zone_id
    evaluate_target_health = true
  }
}
