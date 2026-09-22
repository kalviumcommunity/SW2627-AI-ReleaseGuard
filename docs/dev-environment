Analytics Workspace Setup — Shared Data Product Development Foundation
1. Product Overview

Product Name: Analytics Workspace Setup
Repository Name: analytics-workspace-setup
Primary Branch: main
Development Branch: setup/dev-environment

1.1 Purpose

The purpose of this project is to establish a standardized, reproducible, and professional development environment for a data product team.

The workspace will provide a common foundation for future analytics, dashboards, SQL workflows, machine learning experiments, and predictive insights. It will standardize Python environments, project organization, dependency management, secret handling, and onboarding documentation across the team.

This project does not focus on solving a specific business problem. It focuses on creating the engineering and analytics foundation required before Data Product Development begins.

1.2 Background

The data product team works across multiple business problem areas, including:

Delivery delays
Customer churn
Payment failures
Operational inefficiencies
Employee performance tracking
Infrastructure monitoring
Sales analytics
User engagement analysis

Although the business problems differ, the teams share common development challenges:

Python packages are installed globally.
Different contributors use different package versions.
Unnecessary files may be committed to Git.
Secrets may be stored directly inside scripts.
Project folders are organized inconsistently.
New contributors have difficulty reproducing the development environment.

A standardized analytics workspace will address these foundational issues before business-specific development begins.

2. Goals and Objectives
2.1 Goals

The project must:

Create an isolated Python virtual environment.
Install and manage the required analytics dependencies.
Establish a scalable and consistent project directory structure.
Prevent secrets and unnecessary system files from entering version control.
Capture exact Python package versions.
Provide clear onboarding instructions for new contributors.
Make the environment reproducible on another machine.
Establish a Git workflow using a dedicated development branch and pull request.
2.2 Success Criteria

The project will be considered complete when:

A working Python virtual environment has been created.
All required dependencies are installed successfully.
The required directory structure exists.
Each required directory contains documentation or a .gitkeep file.
.gitignore excludes required files and directories.
requirements.txt contains the installed dependencies and versions.
requirements.txt successfully installs in a clean environment.
README.md provides complete setup instructions.
.env.example documents required environment variables.
No real .env file or venv/ directory is committed.
Changes are committed to setup/dev-environment.
A pull request is opened against main.
A 3–5 minute video demonstrates the required implementation and workflow.
3. Scope
3.1 In Scope

This project includes:

Python virtual environment setup
Dependency installation
Project directory organization
Git ignore configuration
Dependency freezing
Environment variable documentation
README documentation
Git branching and pull request workflow
Environment reproducibility testing
Video documentation
3.2 Out of Scope

The following are not part of this assignment:

Business analytics
Dashboard development
SQL analysis
Predictive modeling
Production deployment
Cloud infrastructure
Database implementation
Data pipeline development
Business-specific datasets
Machine learning model development
4. Technical Requirements
4.1 Python Environment

The project must use Python's built-in venv module to create an isolated environment.

macOS/Linux
python3 -m venv venv
Windows
python -m venv venv

The environment must be activated before installing project dependencies.

macOS/Linux
source venv/bin/activate
Windows
venv\Scripts\activate
5. Dependency Requirements

The following packages must be installed:

pandas
numpy
matplotlib
seaborn
jupyter
scikit-learn
python-dotenv
openpyxl

Installation command:

pip install pandas numpy matplotlib seaborn jupyter scikit-learn python-dotenv openpyxl

The environment must be validated using:

python -c "import pandas; print(pandas.__version__)"

The command must execute successfully without import errors.

6. Project Structure

The repository must follow this structure:

analytics-workspace-setup/
│
├── data/
│   ├── raw/
│   │   └── README.md
│   │
│   └── processed/
│       └── README.md
│
├── notebooks/
│   └── README.md
│
├── scripts/
│   └── README.md
│
├── output/
│   └── README.md
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
6.1 Directory Requirements
data/raw/

Contains original, unmodified datasets obtained from source systems or external sources.

data/processed/

Contains cleaned, transformed, or prepared datasets generated from raw data.

notebooks/

Contains Jupyter notebooks used for exploration, analysis, experimentation, and documentation.

scripts/

Contains reusable Python scripts and automation code that should run independently of notebooks.

output/

Contains generated outputs such as reports, exported files, charts, or other analysis artifacts.

Each directory must contain at least one tracked file so Git maintains the directory structure.

7. Version Control Requirements
7.1 Development Branch

All work must be completed on:

git checkout -b setup/dev-environment

The main branch should not be used directly for implementation.

7.2 Git Workflow

The expected workflow is:

main
  │
  └── setup/dev-environment
          │
          ├── Environment setup
          ├── Folder structure
          ├── .gitignore
          ├── requirements.txt
          └── Documentation
                    │
                    ▼
              Pull Request
                    │
                    ▼
                  main
8. .gitignore Requirements

A .gitignore file must be created at the repository root.

At minimum, it must exclude:

venv/
.venv/
.env

__pycache__/
*.pyc

.ipynb_checkpoints/

.DS_Store
Thumbs.db

The purpose of the .gitignore is to prevent local development artifacts, secrets, generated files, and operating-system-specific files from being committed.

A more comprehensive Python/Jupyter .gitignore may be generated using an appropriate template and customized for this project.

The configuration must be tested using Git status to confirm that the virtual environment and other ignored files do not appear as untracked project files.

9. Environment Variables and Secret Management

The project must use environment variables for secrets and configuration values that should not be committed to source control.

9.1 .env

The actual .env file may contain local secrets and configuration values.

It must not be committed to Git.

Example:

DATABASE_URL=your_database_url
API_KEY=your_api_key

The exact variables should be adjusted based on future project requirements.

9.2 .env.example

A .env.example file must be committed to the repository.

It should document the expected environment variable structure using placeholder values rather than real credentials.

Example:

DATABASE_URL=your_database_url
API_KEY=your_api_key

A new contributor should be instructed to copy:

.env.example

to:

.env

and replace the placeholder values with their own local configuration.

10. Dependency Management

A requirements.txt file must be generated from the active virtual environment.

Command:

pip freeze > requirements.txt

The resulting file must contain package names and exact installed versions.

Example format:

numpy==<version>
pandas==<version>
matplotlib==<version>
...

The actual versions must be generated from the environment rather than manually entered.

10.1 Reproducibility Test

A second virtual environment must be created outside the project directory.

The dependency file must then be tested using:

pip install -r requirements.txt

The installation must complete without errors.

This confirms that another developer can reproduce the project's Python dependencies.

11. README Requirements

A root-level README.md must be created.

The README must contain the following sections.

11.1 Project Description

Explain:

What the workspace is.
Why it exists.
How it supports future analytics and data product development.
11.2 Setup

The setup section must provide numbered instructions for:

Cloning the repository.
Entering the project directory.
Creating the virtual environment.
Activating the environment.
Installing dependencies.
Configuring environment variables.

Both macOS/Linux and Windows commands must be provided.

11.3 Project Structure

The README must list each project directory and explain its purpose in one sentence.

11.4 Notes

The Notes section must explain:

Environment variables are stored locally in .env.
.env must not be committed.
.env.example contains the expected variable structure.
New contributors should copy .env.example to .env.
Contributors must provide their own environment-specific values.
12. Onboarding Requirement

The README must be written so that a new contributor can reproduce the development environment without assistance.

The onboarding test should follow this scenario:

A new teammate receives only the repository URL. They clone the repository and follow the README without asking the original developer any questions.

The documentation passes when the teammate can successfully:

Clone the repository.
Create the virtual environment.
Activate it.
Install dependencies.
Configure environment variables.
Understand the folder structure.
Begin working in the project.
13. Git Commit and Push Requirements

After completing the implementation, all files must be staged:

git add .

The required commit message is:

git commit -m "setup: create venv, folder structure, gitignore, requirements.txt, and README"

The branch must then be pushed:

git push origin setup/dev-environment
14. Pull Request Requirements

A pull request must be opened from:

setup/dev-environment

to:

main

The PR must contain the complete implementation.

The PR diff must visibly include:

README.md
.gitignore
.env.example
requirements.txt
Project directories and their documentation files

The PR must not contain:

venv/
.venv/
.env
Real API keys
Passwords
Database credentials
Other sensitive secrets
15. Video Documentation Requirements

A 3–5 minute screen-share video must accompany the GitHub PR submission.

The video must demonstrate all five required areas.

15.1 Virtual Environment

Explain:

What a Python virtual environment is.
Why isolation is important.
Why a shared data team should avoid installing project dependencies globally.
15.2 Project Structure

Walk through:

data/raw/
data/processed/
notebooks/
scripts/
output/

Explain what belongs in each directory and why the directories are separated.

15.3 Requirements

Show:

requirements.txt

Explain:

What the file contains.
Why exact package versions matter.
How it can be regenerated using:
pip freeze > requirements.txt
15.4 Gitignore and Secrets

Show:

.gitignore

Explain why the following must be excluded:

venv/
.env
Python cache files
Jupyter notebook checkpoints
Operating-system artifacts
15.5 Fresh Environment Setup

Answer the following question in the video:

How would a new teammate replicate this environment from scratch after performing a fresh Git clone?

The explanation should cover the complete workflow from cloning the repository through activating the environment and installing dependencies.

16. Submission Requirements

Two items must be submitted together.

16.1 GitHub Pull Request

The PR URL must follow this format:

https://github.com/YOUR-USERNAME/analytics-workspace-setup/pull/[number]

The PR must be publicly accessible.

The repository must demonstrate that:

The virtual environment is not committed.
No real .env file is committed.
requirements.txt exists.
.gitignore exists.
The required folder structure exists.
README.md exists.
The implementation is contained in the appropriate development branch.
16.2 Video

The video must:

Be 3–5 minutes long.
Be a screen recording.
Cover all five required rubric areas.
Be uploaded to Google Drive.
Have sharing configured as "Anyone with the link can view."
Be tested in a private/incognito browser window before submission.
17. Acceptance Criteria
ID	Requirement	Acceptance Criteria
AC-01	Virtual Environment	A working venv environment can be created and activated on the supported platforms.
AC-02	Dependencies	All eight required packages install successfully.
AC-03	Python Validation	The pandas import/version command executes without errors.
AC-04	Folder Structure	All required directories exist and contain tracked documentation or .gitkeep files.
AC-05	.gitignore	Required environment, cache, notebook, and OS artifacts are ignored.
AC-06	Requirements	requirements.txt contains exact package versions generated using pip freeze.
AC-07	Reproducibility	Dependencies can be installed successfully in a clean virtual environment.
AC-08	README	README contains description, setup, structure, and notes sections.
AC-09	Environment Variables	.env.example exists and .env is excluded from version control.
AC-10	Documentation	A new teammate can reproduce the environment using only the README.
AC-11	Git Workflow	Implementation exists on setup/dev-environment.
AC-12	Pull Request	A PR exists from setup/dev-environment to main.
AC-13	Security	No real secrets or credentials are committed.
AC-14	Video	A 3–5 minute video covers all five required explanation areas.
AC-15	Submission	Public GitHub PR and Google Drive video links are submitted together.