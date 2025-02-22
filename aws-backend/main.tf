module "lambda" {
  source = "./modules/lambda"

  lambda_role_arn = aws_iam_role.lambda_role.arn
}

module "api_gw" {
  source = "./modules/api_gateway"

  api_lambda_invoke_arn = module.lambda.api_lambda_invoke_arn
  api_lambda_name       = module.lambda.api_lambda_name
}
