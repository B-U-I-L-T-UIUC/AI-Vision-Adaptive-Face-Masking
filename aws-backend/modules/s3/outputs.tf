# output "web_bucket_origin_id" {
#     value = aws_s3_bucket.web_bucket.origin
# }

output "web_bucket_region_domain_name" {
    value = aws_s3_bucket.web_bucket.bucket_regional_domain_name
}
