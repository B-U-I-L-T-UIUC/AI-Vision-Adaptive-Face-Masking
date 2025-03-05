module "lambda" {
  source = "./modules/lambda"

  lambda_role_arn = aws_iam_role.lambda_role.arn
}

module "api_gw" {
  source = "./modules/api_gateway"

  api_lambda_invoke_arn = module.lambda.api_lambda_invoke_arn
  api_lambda_name       = module.lambda.api_lambda_name
}

module "data_s3" {
  source = "./modules/data_s3"
}

module "web_app_s3" {
  source = "./modules/web_app_s3"

  cloudfront_arn = module.web_app_cloudfront.cloudfront_arn
}

module "web_app_cloudfront" {
  source = "./modules/cloudfront"

  web_bucket_region_domain_name = module.web_app_s3.web_bucket_region_domain_name
  web_bucket_name               = module.web_app_s3.web_bucket_name
}