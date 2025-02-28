output "web_bucket_name" {
    value = aws_s3_bucket.web_bucket.id
}

output "web_bucket_region_domain_name" {
  value = aws_s3_bucket.web_bucket.bucket_regional_domain_name
}
