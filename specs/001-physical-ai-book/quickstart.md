# Quickstart Guide for Book Contributors

**Purpose**: This guide provides essential steps for new contributors to set up their development environment and begin contributing content to the "Physical AI & Humanoid Robotics" technical book.

**Date**: 2025-12-10
**Feature**: 001-physical-ai-book
**Toolchain**: Docusaurus v3.9, Git

---

## 1. Prerequisites

Before you begin, ensure you have the following installed:

*   **Node.js** (LTS version, includes npm) - Required for Docusaurus.
*   **Git** - For version control and repository management.
*   **PowerShell** (on Windows) or **Bash** (on Linux/macOS) - For running automation scripts.
*   **A text editor or IDE** (e.g., VS Code) - Recommended for content and code editing.

## 2. Clone the Repository

First, clone the book's repository to your local machine:

```bash
git clone <repository-url>
cd Physical-AI-&-Humanoid-Robotics-Textbook
```

Replace `<repository-url>` with the actual URL of the Git repository.

## 3. Install Docusaurus Dependencies

Navigate to the repository root and install Docusaurus dependencies:

```bash
npm install
```

## 4. Run Docusaurus Locally

You can run a local development server to preview your changes in real-time:

```bash
npm run start
```

This will typically open a browser window at `http://localhost:3000`. Any changes you make to the `.mdx` files in the `docs/` directory will automatically refresh the browser.

## 5. Adding/Editing Chapters

*   Chapters are located in the `docs/` directory, organized by modules (e.g., `docs/module1/chapter1.mdx`).
*   Each chapter must follow the structure defined in the project's Constitution: Concept Explanation → Diagram/Code → Applied Example → References.
*   Ensure each chapter `_category_.json` for proper sidebar and navigation.
*   All chapters must be written in Markdown (or MDX for advanced features).

## 6. Integrating Code Examples

*   All runnable code examples should be placed in the `code/` directory, following its internal structure (e.g., `code/ros2_ws/src/`).
*   Refer to code examples from your `.mdx` files using relative paths.
*   Ensure your code examples are well-commented and include clear instructions for setup and execution.

## 7. Version Control Best Practices

*   Always create a new branch for your work: `git checkout -b <your-feature-branch-name>`
*   Commit changes frequently with clear, descriptive commit messages.
*   Pull the latest changes from `main` before pushing your own work: `git pull origin main`
*   Push your branch to the remote: `git push origin <your-feature-branch-name>`
*   Create a Pull Request (PR) for review once your changes are ready.

## 8. Docusaurus Build

To build the static website files for deployment:

```bash
npm run build
```

The generated static files will be located in the `build/` directory.

---
**Need Help?** Refer to the official [Docusaurus Documentation](https://docusaurus.io/docs) for detailed information.
