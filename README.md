# py-microservice

This repository serves as a comprehensive guide to the best practices for Python development within a microservices architecture. It aims to provide developers with clear, actionable insights and examples for building scalable, maintainable, and efficient microservices using Python.

# Clean architecture or Hexagonal architecture or whatever architecture

Choose your own destiny. There is no one-size-fits-all solution. The most important principles are: maintaining consistency, aligning with the team's skills, and ensuring enjoyment in the work process.

Here, what we are looking it's common technical considerations that can be applied to all architectures.

For this example, we will use a custom kiss architecture, only for the sake of simplicity and ready to extends it with your own architecture.

# Feature Overview

- Code Structure and Organization: Recommended patterns for structuring Python microservices projects.
- API Design: Best practices for creating APIs
- Testing Strategies: Unit, integration, and end-to-end testing techniques for microservices.
- CI/CD Pipelines: Guidelines for automating build, test, and deployment processes.
- Observability: Logging, metrics, and distributed tracing setups.
- Security: Authentication, authorization, and secure communication between services.
- Performance Optimization: Tips for enhancing the performance of Python-based microservices
- Task Scheduling: Techniques for scheduling and executing background tasks.
- Containerization: Dockerizing Python microservices with development and production configurations.

# Packaging and Dependency Management

There is a lot of tools to manage dependencies in Python. The most common are `pip`, `poetry`, `conda`, `uv`, etc.

Were are looging for a simple, fast and efficient way to manage dependencies.

# Security

This project includes a basic security setup using Keycloak as an identity provider. We can't avoid talking of microservices without talking about security and the main protocols to use are OAuth2 and OpenID Connect.

# Code Structure and Organization

The main goal of this section is to provide common patterns :

- Basic python project structure
- Inversion Of Control
- Configuration management

# References

- UV, Packaging and project manager : https://astral.sh/blog/uv
- UV, Usefull guide : https://medium.com/@gnetkov/start-using-uv-python-package-manager-for-better-dependency-management-183e7e428760
- Fastapi, Python web framework : https://fastapi.tiangolo.com/
- Loguru, Python logging library : https://github.com/Delgan/loguru
- Loguru, usefull uvicorn integration : https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
- vscode-python, very good pratices here : https://github.com/microsoft/vscode-python/tree/main/.vscode
- keycloak with usefull docker integration : https://github.com/little-pinecone/keycloak-in-docker
- PyJWT : https://pyjwt.readthedocs.io/en/latest/usage.html
- 12-Factor : https://12factor.net/, https://github.com/twelve-factor/twelve-factor
