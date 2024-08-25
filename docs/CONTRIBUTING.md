# Contributing

## Development Setup

To contribute to the Language Learning AI Companion project, follow these steps to set up your development environment:

### Prerequisites

Make sure you have the following installed on your local machine:

- [Docker](https://www.docker.com/)
- [VS Code](https://code.visualstudio.com/) or any preferred code editor
  - Note: we provide a devcontainer configuration for VS Code for easy setup.

### Steps

1. Clone the repository to your local machine.
2. Open the project in VS Code.
3. Click on the "Reopen in Container" prompt to open the project in a Docker container.

### Running the Project

Once you have the project set up in the Docker container, you can run the development server with the following command:

```bash
python manage.py runserver
```

The project will be accessible at `http://localhost:8000/`.

### Database Setup

On the first run, you will need to set up the database. Run the following commands to apply migrations and create a superuser:

```bash
python manage.py migrate
```

Whenever you make changes to the models, run the following command to create new migrations:

```bash
python manage.py makemigrations
```

After creating new migrations, run the `migrate` command again to apply the changes to the database.


### Creating a Superuser

In order to access the Wagtail admin interface, you will need to create a superuser account. To create a superuser, run the following command and follow the prompts:

```bash

To create a superuser for the Wagtail admin interface, run the following command and follow the prompts:

```bash
python manage.py createsuperuser
```

### Making Changes

When making changes to the project, follow these best practices:

- Create a new branch for each feature or bug fix.
- Write clear and concise commit messages.
- Keep commits focused on a single change.
- Push your changes to your fork and submit a pull request to the main repository.
- Respond to any code review feedback and make necessary changes.
- Once approved, your changes will be merged into the main branch.
