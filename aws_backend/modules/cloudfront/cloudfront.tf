locals {
  s3_origin_id = "${var.web_bucket_name}-origin"
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name              = var.web_bucket_region_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.bucket_control.id
    origin_id                = local.s3_origin_id
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "B[U]ILT EOH Project Website"
  default_root_object = "index.html"
  price_class         = "PriceClass_100"

  aliases = ["eoh.built-illinois.org"]

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.s3_origin_id
    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  # needed due to the way react web apps route
  custom_error_response {
    error_code            = 403
    error_caching_min_ttl = 10
    response_code         = 200
    response_page_path    = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US", "CA", "GB", "DE"]
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
    ssl_support_method = "sni-only"
    acm_certificate_arn = "arn:aws:acm:us-east-1:242201276922:certificate/7c268576-5015-4f4a-b7a2-7d5ae74ad8e0"
  }
}

resource "aws_cloudfront_origin_access_control" "bucket_control" {
  name                              = "bucket-control"
  description                       = "Bucket Access Policy for EOH web app"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}