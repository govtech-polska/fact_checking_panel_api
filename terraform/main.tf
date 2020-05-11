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


resource "aws_iam_user" "panel" {
  name = "sfnf-panel-${var.environment}-s3"
  path = "/system/"
}

resource "aws_iam_access_key" "panel" {
  user = "${aws_iam_user.panel.name}"
}

resource "aws_iam_user_policy" "panel" {
  name = "sfnf-panel-${var.environment}-ses"
  user = "${aws_iam_user.panel.name}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "ses:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
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
  container_cpu                = 1024
  container_memory             = 2048
  container_memory_reservation = 2048
  container_port               = 8000
  internal                     = false
  certificate_arn              = var.certificate_arn
  environment = [
    {
      name  = "POSTGRES_HOST"
      value = var.postgres_host
    },
    {
      name  = "CORS_ORIGIN_ALLOW_ALL"
      value = "True"
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
      value = "${aws_iam_access_key.panel.id}"
    },
    {
      name  = "AWS_SECRET_ACCESS_KEY"
      value = "${aws_iam_access_key.panel.secret}"
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
      value = "${aws_iam_access_key.panel.id}"
    },
    {
      name  = "AWS_SECRET_ACCESS_KEY"
      value = "${aws_iam_access_key.panel.secret}"
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

resource "aws_route53_record" "alb_public_web_endpoint" {
  zone_id = data.aws_route53_zone.selected.zone_id
  name    = var.fqdn
  type    = "A"

  alias {
    name                   = module.service.lb_dns_name
    zone_id                = module.service.lb_zone_id
    evaluate_target_health = true
  }
}
