output "api_lambda_invoke_arn" {
    value = aws_lambda_function.api_lambda.invoke_arn
}

output "api_lambda_name" {
    value = aws_lambda_function.api_lambda.function_name
}