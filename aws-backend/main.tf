module "iam" {
  source = "./resources"
}

module "lambda" {
  source   = "./resources"
  # role_arn = module.iam.lambda_role_arn
}

module "api_gateway" {
  source        = "./resources"
  # lambda_arn    = module.lambda.lambda_arn
  # lambda_invoke = module.lambda.lambda_invoke_arn
}
