# iSEE Bioconductor Deployment Infrastructure

This repository manages the automated deployment of iSEE (interactive SummarizedExperiment Explorer) applications on the Bioconductor infrastructure using Kubernetes.

## Getting Started: Adding New iSEE Instances

### Prerequisites

To add a new iSEE instance, you need:

1. **Dataset File**: An RDS file containing a SummarizedExperiment object, publicly accessible via HTTPS
2. **Configuration Script**: An R script that defines the `initial` variable for iSEE, publicly accessible via HTTPS
3. **Unique ID**: A descriptive identifier for your deployment (will become the subdomain)

### Submit a Pull Request

1. **Fork this repository** on GitHub

2. **Add your dataset** (if new) to `config-dataset.csv`:
   ```csv
   YourDatasetID,Your Dataset Title,https://your-data-url/dataset.rds,"Your dataset description"
   ```

3. **Add your configuration** to `config-initial.csv`:
   ```csv
   YourID,YourDatasetID,YourConfigID,Your Config Title,https://your-config-url/config.R,"Your configuration description",3.21
   ```

4. **Example additions**:
   
   **config-dataset.csv**:
   ```csv
   SingleCellRNA,My Single Cell Study,https://zenodo.org/record/123/mystudy_sce.rds,"Single cell RNA-seq data from my study"
   ```
   
   **config-initial.csv**:
   ```csv
   MyStudy1,SingleCellRNA,MyStudy_Config1,Default View,https://github.com/user/repo/raw/main/isee_config.R,"UMAP + gene expression + metadata table",3.21
   ```

5. **Create a Pull Request** with:
   - **Title**: "Add iSEE instance: [Your ID]"
   - **Description**: Brief description of your dataset and intended use

### Automatic Integration

Once your PR is merged:

1. **Automatic Deployment**: GitHub Actions will automatically deploy your iSEE instance
2. **Subdomain Creation**: Your instance will be available at `yourid.isee.bioconductor.org`
3. **Main Site Integration**: Your configuration will appear in the dropdown menu at `isee.bioconductor.org`

### Verification

After deployment (usually within 5-10 minutes):

1. **Direct Access**: Visit `yourid.isee.bioconductor.org` 
2. **Main Portal**: Check `isee.bioconductor.org` for your dataset in the dropdown
3. **SSL Certificate**: Automatic TLS certificate provisioning via Let's Encrypt

## Administrator Guide

### Kubernetes Infrastructure Requirements

To deploy this system, administrators need a Kubernetes cluster with the following components:

#### Required Components

1. **Ingress Controller**
   - Nginx Ingress Controller (recommended) or equivalent
   - Handles HTTP/HTTPS traffic routing to services
   - Manages SSL termination and domain-based routing

2. **cert-manager**
   - Automatic SSL certificate provisioning via Let's Encrypt
   - Manages certificate lifecycle and renewal
   - Required for HTTPS endpoints

3. **DNS Configuration**
   - Wildcard DNS record: `*.isee.bioconductor.org` → Ingress Controller IP
   - Allows automatic subdomain creation without manual DNS changes

#### GitHub Actions Configuration

The deployment workflow requires a kubeconfig secret in GitHub:

**Add to GitHub Secrets**:
   - Go to repository Settings → Secrets and variables → Actions
   - Add kubeconfig to secret named `KUBECONFIG`, with at least enough permissions to create/delete namespaces, deployments, PVC and service/ingress resources. 

## Architecture Overview

The deployment system creates separate Shiny container deployments in a Kubernetes cluster, where each dataset configuration gets its own dedicated subdomain and resources. This architecture provides:

- **Isolation**: Each iSEE instance runs in its own namespace with dedicated resources
- **Scalability**: Independent scaling per dataset without affecting others
- **Reliability**: Failures in one instance don't impact other deployments
- **Custom URLs**: Each dataset gets a dedicated subdomain (e.g., `allendemo1.isee.bioconductor.org`)

### Deployment Components

Each iSEE application deployment consists of:

1. **Kubernetes Namespace**: `{id}-isee` (e.g., `allendemo1-isee`)
2. **ConfigMap**: Contains the generated `app.R` file with dataset-specific configuration
3. **Deployment**: Runs the Shiny server with the iSEE application
4. **Service**: Exposes the application within the cluster
5. **Ingress**: Provides external access via subdomain with TLS termination

### Container Image

All deployments use the standardized container image: `ghcr.io/almahmoud/iseeindex:devel`

This image contains:
- R environment with iSEE/iSEEindex and dependencies
- Shiny server configuration
- Base application template

## Configuration Management

### CSV Configuration Files

The deployment system is driven by two CSV files that separate dataset definitions from instance configurations. This separation allows:

- **Dataset Reuse**: Multiple configurations can reference the same dataset
- **Easier Management**: Dataset URLs and descriptions are maintained in one place
- **Version Control**: Track changes to datasets vs configurations separately

#### `config-dataset.csv`
Defines available datasets:

| Column | Description | Example |
|--------|-------------|---------|
| `datasetID` | Unique dataset identifier | `ReprocessedAllen` |
| `datasetTitle` | Human-readable dataset name | `ReprocessedAllen` |
| `datasetURI` | URL to the dataset RDS file | `https://raw.githubusercontent.com/...` |
| `datasetDescription` | Dataset description | `"Reprocessed Allen Data."` |

#### `config-initial.csv`
Defines iSEE instance configurations:

| Column | Description | Example |
|--------|-------------|---------|
| `ID` | Unique identifier for the deployment | `AllenDemo1` |
| `datasetID` | References dataset from config-dataset.csv | `ReprocessedAllen` |
| `configID` | Configuration identifier | `Allen_Config1` |
| `configTitle` | Configuration title | `InitialConfig1` |
| `configURI` | URL to the initial configuration R script | `https://raw.githubusercontent.com/...` |
| `configDescription` | Configuration description | `"PCA plot + feature assay plot"` |
| `biocversion` | Bioconductor version | `3.21` |

### Template Files

The system uses two template files in `.github/templates/`:

#### `app.R`
```r
sce <- readRDS(url(##PLACEHOLDERDATASETURI##))
source(url(##PLACEHOLDERCONFIGURI##))
iSEE::iSEE(se = sce, initial = initial)
```

#### `isee-deployment.yaml`
Kubernetes deployment manifest with placeholders for:
- `##PLACEHOLDERID##`: Replaced with the lowercase ID
- Namespace, service, and ingress configurations

## Automated Deployment

### GitHub Actions Workflow

The deployment is automated via GitHub Actions (`.github/workflows/deploy-isee-subdomains.yaml`) and triggers on:

- Manual workflow dispatch
- Push events that modify `config-dataset.csv` or `config-initial.csv`

### Deployment Process

1. **CSV Parsing**: Python script joins data from both CSV files and extracts ID, datasetURI, and configURI for each configuration
2. **Template Processing**: `sed` replaces placeholders in templates with actual values
3. **Kubernetes Resources**:
   - Create namespace: `{id}-isee`
   - Create configmap: `{id}-isee-app` with the processed `app.R`
   - Apply deployment manifest to the namespace
4. **Result**: Application accessible at `{id}.isee.bioconductor.org`


## Support

For questions or issues:

1. **Documentation**: Check iSEE documentation at [bioconductor.org/packages/iSEE](https://bioconductor.org/packages/iSEE)
2. **Issues**: Submit GitHub issues for deployment problems
