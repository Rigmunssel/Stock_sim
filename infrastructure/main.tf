# Enable Compute API
resource "google_project_service" "compute" {
  service = "compute.googleapis.com"
}

# Simple VPC
resource "google_compute_network" "vpc" {
  name                    = "webapp-vpc"
  auto_create_subnetworks = true
  depends_on              = [google_project_service.compute]
}

# Open HTTP + your app ports; lock down later
resource "google_compute_firewall" "allow-http-app" {
  name    = "allow-http-app"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22","80","8080","5001"]
  }
  source_ranges = ["0.0.0.0/0"]
}

# VM
resource "google_compute_instance" "vm" {
  name         = "docker-host"
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "projects/debian-cloud/global/images/family/debian-12"
      size  = 20
    }
  }

  network_interface {
    network = google_compute_network.vpc.name
    access_config {} # ephemeral public IP
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    set -euxo pipefail

    apt-get update
    apt-get install -y ca-certificates curl gnupg git

    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
      | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Fetch app
    mkdir -p /opt/app
    cd /opt/app
    if [ ! -d repo ]; then
      git clone "${var.repo_url}" repo
    fi
    cd repo

    # Adjust BACKEND_URL in docker-compose to use this VM's public IP
    EXT_IP=$(curl -s -H "Metadata-Flavor: Google" \
      http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip)

    if [ -f docker-compose.yml ]; then
      sed -i "s|BACKEND_URL=http://localhost:5001|BACKEND_URL=http://$${EXT_IP}:5001|g" docker-compose.yml
    elif [ -f docker-compose.yaml ]; then
      sed -i "s|BACKEND_URL=http://localhost:5001|BACKEND_URL=http://$${EXT_IP}:5001|g" docker-compose.yaml
    fi

    # Optional: expose frontend on port 80 instead of 8080
    sed -i 's/"8080:80"/"80:80"/' docker-compose.yml || true
    sed -i 's/"8080:80"/"80:80"/' docker-compose.yaml || true

    # Start containers
    docker compose pull || true
    docker compose build
    docker compose up -d

    # Auto-restart on reboot
    systemctl enable docker
  EOT

  # Let Terraform read the public IP in outputs
  depends_on = [google_compute_firewall.allow-http-app]
}

output "vm_ip" {
  value = google_compute_instance.vm.network_interface[0].access_config[0].nat_ip
  description = "Public IP of the VM"
}