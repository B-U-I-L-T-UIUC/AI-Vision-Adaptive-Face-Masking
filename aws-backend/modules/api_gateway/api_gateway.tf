resource "aws_apigatewayv2_api" "http_api" {
  name          = "eoh-face-masking-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.api_lambda_name
  principal     = "apigateway.amazonaws.com"
}

module "v1_path" {
  source = "./v1_path"

  api_gw_http_id = aws_apigatewayv2_api.http_api.id

  api_lambda_invoke_arn = var.api_lambda_invoke_arn
}