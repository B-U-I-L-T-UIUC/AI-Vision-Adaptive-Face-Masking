
resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "iot_publish_policy" {
  name        = "iot_publish_policy"
  description = "Policy allowing Lambda to publish to user-requests topic in IoT Core"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "iot:Publish"
        Resource = "arn:aws:iot:us-east-1:${data.aws_caller_identity.current.account_id}:topic/user-requests"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.iot_publish_policy.arn
}
