resource "aws_apigatewayv2_integration" "lambda_api" {
  api_id           = var.api_gw_http_id
  integration_type = "AWS_PROXY"
  integration_uri  = var.api_lambda_invoke_arn
}

# POST /v1/image/{userId}
resource "aws_apigatewayv2_route" "image_upload" {
  api_id    = var.api_gw_http_id
  route_key = "POST /v1/image/{userId}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api.id}"
}

# POST /v1/feature/{userId}
resource "aws_apigatewayv2_route" "avatar_feature_change" {
  api_id    = var.api_gw_http_id
  route_key = "POST /v1/feature/{userId}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api.id}"
}

# GET /v1/user/{userId}
resource "aws_apigatewayv2_route" "user_data" {
  api_id    = var.api_gw_http_id
  route_key = "GET /v1/user/{userId}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api.id}"
}

# GET /v1/mask
resource "aws_apigatewayv2_route" "get_masks" {
  api_id    = var.api_gw_http_id
  route_key = "GET /v1/mask"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api.id}"
}

# POSt /v1/mask
resource "aws_apigatewayv2_route" "upload_mask" {
  api_id    = var.api_gw_http_id
  route_key = "POST /v1/mask"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api.id}"
}
