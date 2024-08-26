# Deploy

This document outlines the process for deploying the application to DigitalOcean App Platform.

## Prerequisites

Ensure you have:

- A DigitalOcean account
- A GitHub account
- A GitHub repository with the application code

## Deployment Steps

### 1. Set up DigitalOcean Space

- Create a new Space in your DigitalOcean account
- Generate Access Key and Secret Key for the Space
- Configure CORS for the Space with the following settings:
  - Origin: Your deployment domain name (e.g., yourdomain.com)
  - Allowed Methods: GET
  - Allowed Headers:
    - Access-Control-Allow-Origin
    - Referer
  - Access Control Max Age: 600
- Note the Space's Endpoint URL

### 2. Create a DigitalOcean App

- Start the app creation process in the DigitalOcean dashboard
- Connect your GitHub account and select the repository with your application code

### 3. Configure the App

- Set up the following environment variables:
  - `DJANGO_ALLOWED_HOSTS`: Your app's domain name
  - `USE_SPACES`: Set to `True`
  - `AWS_ACCESS_KEY_ID`: Access Key from your DigitalOcean Space
  - `AWS_SECRET_ACCESS_KEY`: Secret Key from your DigitalOcean Space
  - `AWS_S3_ENDPOINT_URL`: Endpoint URL of your DigitalOcean Space
  - `AWS_STORAGE_BUCKET_NAME`: Name of your DigitalOcean Space
  - `DJANGO_SECRET_KEY`: A secure random string for Django

- Add a PostgreSQL database component to your app

### 4. Deploy

- Initiate the deployment process for your app (if it is not automatically triggered)

## Post-Deployment

After successful deployment, ensure to:

- Verify that all components are running correctly
- Test the application functionality
- Set up any necessary DNS configurations

Remember to refer to DigitalOcean's documentation for the most up-to-date information on specific steps or if you encounter any issues during the deployment process.
