data "aws_caller_identity" "current" {}

data "aws_ecr_repository" "priceChecker" {
  name                 = "price-checker"
}

data "aws_iam_role" "docker-price-checker-role" {
  name = "docker-price-checker_tf-role-cu47mrbj"
}

resource "aws_lambda_function" "docker-price-checker_tf" {
  function_name = "docker-price-checker_tf"
  timeout           = 180 # seconds
  image_uri         = "${data.aws_ecr_repository.priceChecker.repository_url}:latest"
  package_type      = "Image"
  memory_size       = "1024"
  
  ephemeral_storage {
    size = "800"
  }

  role = data.aws_iam_role.docker-price-checker-role.arn
}

resource "aws_ecr_lifecycle_policy" "priceCheckerPolicy" {
    repository = data.aws_ecr_repository.priceChecker.name
    
    policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Expire every images except latest",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 1
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

data "aws_iam_role" "schedulerRole" {
  name = "Amazon_EventBridge_Scheduler_LAMBDA_b4c9a7d45d"
}

resource "aws_scheduler_schedule" "FlightPriceCheckLambdaSchedule" {
  name       = "FlightPriceCheckLambdaTF"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 */6 ? * * *)"

  schedule_expression_timezone = "America/New_York"

  start_date = "2024-07-27T05:50:00Z"

  target {
    arn      = aws_lambda_function.docker-price-checker_tf.arn
    role_arn = data.aws_iam_role.schedulerRole.arn

    retry_policy {
    maximum_event_age_in_seconds = 900
    maximum_retry_attempts = 1
    }
  }
}
