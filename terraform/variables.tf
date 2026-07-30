variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "mlops-cluster"
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "sentiment-api"
}