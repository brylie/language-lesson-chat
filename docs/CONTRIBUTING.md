# Contributing

Welcome to the Language Learning AI Companion project! We're excited to have you contribute to our open-source initiative. This document outlines our development philosophy, technology choices, and guidelines for contributors. It also provides instructions for setting up your development environment and making changes to the project.

- [Contributing](#contributing)
  - [Development Philosophy and Guidelines](#development-philosophy-and-guidelines)
    - [Core Philosophies](#core-philosophies)
      - [Simplicity](#simplicity)
      - [Sustainability](#sustainability)
      - [Progressive Enhancement](#progressive-enhancement)
    - [Technology Choices and Rationale](#technology-choices-and-rationale)
      - [Core Technologies](#core-technologies)
    - [Frontend Development](#frontend-development)
      - [Development Environment](#development-environment)
      - [Deployment](#deployment)
    - [Benefits of Our Approach](#benefits-of-our-approach)
    - [Guidelines for Contributors](#guidelines-for-contributors)
  - [Development Setup](#development-setup)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
    - [Running the Project](#running-the-project)
    - [Database Setup](#database-setup)
    - [Creating a Superuser](#creating-a-superuser)
    - [Making Changes](#making-changes)


## Development Philosophy and Guidelines

Our project is built on the principles of Simplicity, Sustainability, and Progressive Enhancement. These guiding philosophies inform our technology choices and development practices, ensuring a robust, maintainable, and future-proof application.

### Core Philosophies

#### Simplicity
We strive to keep our technology stack and development processes as simple as possible. This approach reduces cognitive load on developers, minimizes potential points of failure, and makes our project more accessible to new contributors.

#### Sustainability
Our choices are made with long-term sustainability in mind. We prioritize mature, well-established technologies and practices that have stood the test of time and are likely to remain relevant and supported for years to come.

#### Progressive Enhancement
We build our application to be functional and accessible at its core, then enhance it with additional features and interactivity where beneficial. This ensures a solid foundation and broad compatibility.

### Technology Choices and Rationale

#### Core Technologies

1. **HTML, CSS, and JavaScript**: We rely primarily on these standard web platform languages. They are designed for backward compatibility and have proven their longevity. This choice ensures our codebase remains stable and doesn't require frequent large-scale refactoring.

2. **Python/Django/Wagtail CMS**: Our backend is built on this mature ecosystem. It provides a robust foundation with a large community, extensive features, and long-term support, reducing the need for custom solutions or frequent major updates.

### Frontend Development

1. **Vanilla JavaScript**: We use standard JavaScript without preprocessors, bundlers, or transpilers. This simplifies our build process and ensures maximum browser compatibility.

2. **Standard CSS**: We avoid CSS preprocessors, instead leveraging modern CSS features like CSS variables when needed. This approach keeps our styles simple and easy to maintain.

3. **Bootstrap CSS Framework**: We've chosen Bootstrap for UI components and responsive design due to its longevity, wide adoption, and continual adaptation to modern web capabilities.

4. **HTMX**: This framework allows us to implement dynamic behaviors with minimal client-side JavaScript, leveraging server-side state and templating for most functionality.

5. **Progressive Enhancement**: When additional client-side interactivity is necessary, we consider libraries that support progressive enhancement without requiring preprocessing. Potential options include Vue.js or Stimulus, which can be included via CDN or simple script tags.

#### Development Environment

We use Docker and Devcontainers to provide a consistent, easily reproducible development environment. This setup abstracts away dependencies and simplifies the onboarding process for new developers.

#### Deployment

We provide specific instructions for deploying to DigitalOcean App Platform, a PaaS solution that offers sustainable pricing and streamlined deployment processes. This choice allows the team to focus on product development rather than infrastructure management.

### Benefits of Our Approach

1. **Reduced Complexity**: By minimizing the number of technologies and avoiding preprocessors or transpilers, we keep our development process straightforward and accessible.

2. **Long-term Stability**: Our choice of mature, widely-adopted technologies helps ensure the longevity and stability of our codebase.

3. **Easier Maintenance**: Standard web technologies and a simple stack make our code easier to understand, debug, and maintain over time.

4. **Improved Performance**: By keeping our client-side code lean and leveraging server-side rendering where possible, we can deliver a fast, efficient user experience.

5. **Accessibility**: Our progressive enhancement approach ensures that core functionality is available to all users, regardless of their browser capabilities.

6. **Focus on Core Goals**: By simplifying our technology stack and leveraging PaaS for deployment, we free up resources to focus on our core product and business objectives.

### Guidelines for Contributors

When contributing to this project, please keep the following in mind:

1. Prioritize simplicity and readability in your code.
2. Leverage existing features of our chosen frameworks before introducing new dependencies.
3. When adding interactivity, consider whether it can be achieved through HTMX or simple JavaScript before reaching for more complex solutions.
4. Ensure that new features degrade gracefully for users without JavaScript or with older browsers.
5. Maintain consistency with the existing codebase in terms of style and approach.
6. When in doubt, refer back to our core philosophies of Simplicity, Sustainability, and Progressive Enhancement.

By adhering to these principles and guidelines, we aim to create a robust, maintainable application that can stand the test of time and deliver value to our users for years to come.

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
