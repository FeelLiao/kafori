# Contribution Guidelines for kafori

Thank you for your interest in contributing to kafori! We appreciate your help in making this project better. Please follow these guidelines to ensure a smooth contribution process.

## How to Contribute

1. **Fork the Repository**: Start by forking the kafori repository on GitHub. This will create a copy of the repository under your account.

2. **Clone Your Fork**: Clone your forked repository to your local machine:
   ```
   git clone https://github.com/feelliao/kafori.git
   ```

3. **Create a Branch**: Create a new branch for your feature or bug fix:
   ```
   git checkout -b my-feature-branch
   ```

4. **Make Changes**: Make your changes to the codebase. Be sure to write clear, concise commit messages.

5. **Run Tests**: Before submitting your changes, run the existing tests to ensure your changes don't break anything:
   ```
   pytest
   ```

6. **Submit a Pull Request**: Once you're satisfied with your changes, push your branch to your forked repository:
   ```
   git push origin my-feature-branch
   ```
   Then, go to the original kafori repository and submit a pull request.

## Development Environment

Before you start contributing, it's important to set up a development environment that mirrors the production setup as closely as possible. This will help you test your changes effectively and ensure compatibility with the existing codebase. This project uses `conda` for environment management and `poetry` for dependency management. You can find the environment configuration in the `kafori_conda.yml` file.

If you are new to `conda` or `poetry`, here are some brief instructions to help you get started:
- **Conda**: A package manager that simplifies the management of dependencies and environments in Python.
- **Poetry**: A dependency management tool for Python that helps you manage your project's dependencies and packaging.

You can find more information about these tools in their respective documentation:
- [Conda Documentation](https://docs.conda.io/projects/conda/en/latest/)
- [Poetry Documentation](https://python-poetry.org/docs/)

We recommend using the third-party distribution of `conda` called [miniforge](https://conda-forge.org/download/) to manage your environments and dependencies. After installing miniforge, you can set a mirror to faster download packages. Please refer to the [tsinghua mirror for anaconda]https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/ for instructions on how to set up a mirror.

To set up a development environment for kafori, follow these steps:

1. **Set Up a Virtual Environment**: It's a good practice to use a virtual environment for Python projects. `conda` environments are recommended for this project.
You can create and activate a virtual environment using:
   ```
   conda env create -f kafori_conda.yml
   conda activate kafori
   ```

1. **Install Dependencies**: Make sure you have all the required dependencies installed. You can use a package manager called `poetry` to install them:
   ```
   poetry install
   ```

3. **Run the Development Server**: Once your environment is set up, you can run the development server to test your changes:
   ```
   fastapi run backend/main.py
   ```

## Questions?

If you have any questions or need assistance, feel free to reach out to the kafori team.

Thank you for contributing to kafori!
