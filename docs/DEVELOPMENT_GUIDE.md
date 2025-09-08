# Development Guide

## Project Organization
- Django apps in `apps/`
- Frontend in `frontend/`
- Utilities in `utils/`, `middlewares/`, etc.

## Code Conventions
- Follow PEP8 for Python.
- Use descriptive names for functions, variables, and files.
- Separate responsibilities into apps and modules.

## Workflow
1. Create a branch for each feature/bugfix:
   ```bash
   git checkout -b feature/feature-name
   ```
2. Make small and descriptive commits.
3. Open a Pull Request for review.
4. Use the `workflow.md` file to follow the contribution flow.

## Tests
- Tests in `test/`.
- Run with:
  ```bash
  python manage.py test
  ```
- Write tests for new features.

## Linters and Quality
- Use `flake8`, `black` or similar tools to maintain code standards.

## Tips
- Check the documentation for apps in `docs/`.
- Use environment variables for sensitive settings. 