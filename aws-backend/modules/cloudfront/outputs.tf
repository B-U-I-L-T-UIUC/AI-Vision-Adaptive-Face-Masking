output "cloudfront_arn" {
    value = aws_cloudfront_distribution.s3_distribution.arn
}