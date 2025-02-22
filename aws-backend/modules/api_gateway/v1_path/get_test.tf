resource "aws_apigatewayv2_integration" "lambda" {
  api_id           = var.api_gw_http_id
  integration_type = "AWS_PROXY"
  integration_uri = var.api_lambda_invoke_arn
}

resource "aws_apigatewayv2_route" "lambda" {
  api_id    = var.api_gw_http_id
  route_key = "GET /v1/lambda"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}
