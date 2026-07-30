output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "ecr_repository_url" {
  value = aws_ecr_repository.sentiment_api.repository_url
}

output "configure_kubectl" {
  description = "Run this after apply to connect kubectl"
  value = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.region}"
}
output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
  description = "Use this in GitHub Actions workflow"
}