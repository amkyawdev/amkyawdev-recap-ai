output "eks_cluster_name" {
  description = "EKS Cluster name"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "EKS Cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "eks_cluster_ca_cert" {
  description = "EKS Cluster CA certificate"
  value       = aws_eks_cluster.main.certificate_authority[0].data
  sensitive   = true
}

output "s3_bucket_name" {
  description = "S3 Storage bucket name"
  value       = aws_s3_bucket.storage.bucket
}

output "ecr_backend_repo" {
  description = "Backend ECR repository URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_gpu_worker_repo" {
  description = "GPU Worker ECR repository URL"
  value       = aws_ecr_repository.gpu_worker.repository_url
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}
