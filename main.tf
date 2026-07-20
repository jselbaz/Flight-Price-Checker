data "aws_caller_identity" "current" {}

data "aws_ecr_repository" "priceChecker" {
  name                 = "price-checker"
}

data "aws_iam_role" "docker-price-checker-role" {
  name = "docker-price-checker_tf-role-cu47mrbj"
}

resource "aws_lambda_function" "docker-price-checker_tf" {
  function_name = "docker-price-checker_tf"
  timeout           = 90 # seconds
  image_uri         = "${data.aws_ecr_repository.priceChecker.repository_url}:latest"
  package_type      = "Image"
  memory_size       = "1024"
  
  ephemeral_storage {
    size = "800"
  }


  role = data.aws_iam_role.docker-price-checker-role.arn

  environment {
    variables = {
      FLIGHT1 = "846",
      FLIGHT2 = "856",
      URL1 = "https://www.google.com/travel/flights/booking?tfs=CBwQAhpKEgoyMDI2LTA5LTA1Ih8KA0xHQRIKMjAyNi0wOS0wNRoDREZXKgJETDIDODQ2KAA6AkY5agcIARIDTEdBcgwIAhIIL20vMGYycnFAAUgBcAGCAQsI____________AZgBAsgBAQ&tfu=CmhDalJJZW5KWFdISnZka0pUVkdkQll6VlJlbmRDUnkwdExTMHRMUzB0TFhkbVoyY3lORUZCUVVGQlIzQmtaeTFqVDBaVlh6SkJFZ1ZFVERnME5ob0tDT3gzRUFJYUExVlRSRGdjY094MxICCAAiAA",
      URL2 = "https://www.google.com/travel/flights/booking?tfs=CBwQAhpKEgoyMDI2LTA5LTE1Ih8KA0RGVxIKMjAyNi0wOS0xNRoDTEdBKgJETDIDODU2KAA6AkY5agwIAhIIL20vMGYycnFyBwgBEgNMR0FAAUgBcAGCAQsI____________AZgBAsgBAQ&tfu=CmxDalJJT0dSMVVrWm1WMGRUU1RSQlNtdHJObEZDUnkwdExTMHRMUzB0TFhaMFlYY3lNMEZCUVVGQlIzQmthRU5qUTBKbldrTkJFZ1ZFVERnMU5ob0xDTWlEQVJBQ0dnTlZVMFE0SEhESWd3RT0SAggAIgA"
    }
  }
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
