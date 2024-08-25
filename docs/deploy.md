# Deploy

This document describes steps to deploy the application to a server. Our primary recommendation is to use DigitalOcean App Platform. So, theses steps are for deploying to DigitalOcean App Platform.

## Prerequisites

The following are required to deploy the application:

- A DigitalOcean account
- A GitHub account
- A GitHub repository with the application code
- A DigitalOcean Space

Note: we will create these assets in the following steps.

## Steps

Once you have the prerequisites, follow these steps to deploy the application:

###  Get the DigitalOcean Space credentials

1. Go to the DigitalOcean dashboard.
2. Click on the Spaces link in the left sidebar.
3. Click on the Create a Space button.
4. Fill in the details and click on the Create Space button.
5. Click on the Spaces link in the left sidebar.
6. Click on the name of the space you created.
7. Click on the Settings tab.
8. Click on the Generate Key button.
9. Copy the Access Key and Secret Key.
10. Save the keys in a safe place.
11. Click on the CORS tab.
12. Add the following CORS configuration:

    ```plaintext
    [
        {
            "origin": ["*"],
            "method": ["GET"],
            "max_age": 3600
        }
    ]
    ```
13. Click on the Save CORS Configuration button.
14. Click on the Overview tab.
15. Copy the Endpoint URL.
16. Save the Endpoint URL in a safe place.

### Create a DigitalOcean App

1. Go to the DigitalOcean dashboard.
2. Click on the Apps link in the left sidebar.
3. Click on the Create App button.
4. Click on the GitHub button.
5. Click on the Connect to GitHub button.
6. Click on the Install button.
7. Click on the Complete Setup button.
8. Click on the Create App button.
9. Select the GitHub repository with the application code.

### Configure the DigitalOcean App

1. Click on the Settings tab.
2. Click on the Environment Variables link.
3. Add the following environment variables:

    - `DJANGO_ALLOWED_HOSTS`: The domain name of the app.
    - `USE_SPACES`: `True` - to use DigitalOcean Spaces.
    - `AWS_ACCESS_KEY_ID`: The Access Key from the DigitalOcean Space.
    - `AWS_SECRET_ACCESS_KEY`: The Secret Key from the DigitalOcean Space.
    - `AWS_S3_ENDPOINT_URL`: The Endpoint URL from the DigitalOcean Space.
    - `AWS_STORAGE_BUCKET_NAME`: The name of the bucket in the DigitalOcean Space.
    - `DJANGO_SECRET_KEY`: A random string for the Django secret key.
4. Click on the Save Changes button.
5. Click on the Components tab.
6. Click on the Add Component button.
7. Select the PostgreSQL database.
8. Click on the Next button.
9. Click on the Finish button.
10. Click on the Create Component button.
11. Click on the Deployments tab.
12. Click on the Deploy Now button.
