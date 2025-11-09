## Prerequisites

**For LOCAL testing:**
- Docker 20.10+ 
- Docker Compose 2.0+

**For GCP deployment:**
- GCP CLI
- Terraform 1.0+
- GCP Account with credentials (and billing)


### Install Prerequisites

#### Windows

1. **Docker Desktop** (includes Docker + Docker Compose):  
   - Download: https://docs.docker.com/desktop/install/windows-install/  
   - Run the installer and follow prompts  
   - Restart when prompted  

2. **Google Cloud CLI (gcloud)**:  
   - Download: https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe  
   - Run installer and check **“Add gcloud to PATH”**  
   - Verify:  
     ```bash
     gcloud version
     ```

3. **Terraform**:  
   - Download: https://www.terraform.io/downloads  
   - Extract `terraform.exe` to `C:\Windows\System32\` or add it to PATH  
   - Verify:  
     ```bash
     terraform version
     ```

#### Mac

1. **Docker Desktop** (includes Docker + Docker Compose):  
   - Download: https://docs.docker.com/desktop/install/mac-install/  
   - Drag to Applications folder  
   - Open and follow setup  

2. **Google Cloud CLI**:  
   ```bash
   brew install --cask google-cloud-sdk
   ````

3. **Terraform**:

   ```bash
   brew install terraform
   # OR download from https://www.terraform.io/downloads
   ```

#### Linux

1. **Docker & Docker Compose**:

   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

2. **Google Cloud CLI**:

   ```bash
   sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates gnupg
   echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | \
     sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
   curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
     sudo tee /usr/share/keyrings/cloud.google.gpg >/dev/null
   sudo apt-get update && sudo apt-get install -y google-cloud-cli
   ```

3. **Terraform**:

   ```bash
   cd /tmp
   wget https://releases.hashicorp.com/terraform/1.6.5/terraform_1.6.5_linux_amd64.zip
   unzip terraform_1.6.5_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```


**Verify all installations:**

```bash
docker --version
docker compose version
gcloud version
terraform version
```

## Run Locally
```bash
docker-compose up --build
```

Open on http://localhost:8080

## Deploy to GCP

**Step 1: Authenticate with Google Cloud (first time only)**

```bash
gcloud init
````

Follow prompts:

* Sign in with your Google account
* Choose **Create a new project** or select an existing one
* My **Project ID** is "op-task" 

Then link billing:

```bash
gcloud beta billing accounts list
gcloud beta billing projects link <PROJECT_ID> --billing-account=<ACCOUNT_ID>
```

**Step 2: Set active project**

```bash
gcloud config set project <PROJECT_ID>
```

**Step 3: Enable Terraform credentials**

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project <PROJECT_ID>
```

**Step 4: Set Terraform environment variables**

```bash
export TF_VAR_project_id=$(gcloud config get-value project)
export TF_VAR_repo_url="https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git"
```

**Step 5: Initialize and deploy infrastructure**

Run from the `infrastructure` folder (cd ./infrastructure):

```bash
terraform init
terraform apply -auto-approve
```

Wait 3–5 minutes. Terraform will:

* Enable Compute Engine API
* Create a VPC and firewall
* Launch a VM
* Install Docker + Docker Compose
* Clone the app repo
* Run `docker compose up -d`

**Step 6: Access the app**

After deployment, Terraform outputs:
```
vm_ip = "xx.xx.xx.xx"
```

Visit in browser:
```
http://xx.xx.xx.xx
```

**To remove everything and close the website**
```bash
terraform destroy -auto-approve
```

## High Level Overview

- Python Flask backend
- HTML/CSS/JS frontend with Chart.js  
- 10 stock symbols with realistic demo data
- Complete Docker setup
- Complete Terraform IaC for GCP

## API Endpoints

```
GET /api/health - Health check
GET /api/stocks - List of stocks
GET /api/stock/<symbol> - Get price data
GET /api/message - Hello message
```

## Project Structure

```
web_app/
├── backend/           # Flask API + Dockerfile
├── frontend/          # Web UI + Dockerfile  
├── infrastructure/    # Terraform files
└── docker-compose.yml
```
