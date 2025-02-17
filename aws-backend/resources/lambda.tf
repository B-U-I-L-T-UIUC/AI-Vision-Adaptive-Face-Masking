resource "aws_lambda_function" "my_lambda" {
  function_name    = "MyPythonLambda"
  role            = aws_iam_role.lambda_role.arn
  handler         = "main.lambda_handler"
  runtime         = "python3.9"

  filename        = "${path.module}/../lambda_api/function.zip"
  source_code_hash = filebase64sha256("${path.module}/../lambda_api/function.zip")

  timeout         = 10
  memory_size     = 128
}