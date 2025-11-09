variable "project_id" {}
variable "region"      { default = "europe-north1" }   # Finland
variable "zone"        { default = "europe-north1-a" }
variable "machine_type"{ default = "e2-medium" }
# Public Git repo URL with your docker-compose.yml at repo root
variable "repo_url"    { description = "Git repo URL to clone" }