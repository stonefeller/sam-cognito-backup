## Overview

This document outlines how the Cognito Backup SAM Application is designed to back up user data from an AWS Cognito User Pool to an S3 bucket. The application consists of a Lambda function that retrieves user data from the Cognito User Pool, formats it into a CSV file, and uploads it to the specified S3 bucket. The application is scheduled to run periodically using AWS EventBridge every 12 hours.

## Steps to Follow

### 1. Create a Branch

#### Clone the Repository (if you haven't already):

```git clone <repository-url>```

```cd <repository-directory>```

#### Create a New Branch:

```git checkout -b <your-branch-name>```

---

### 2. Make Your Changes

1. Make the necessary changes to the codebase.

2. **Stage Your Changes:**

    ```git add .```

3. **Commit Your Changes:**

    ```git commit -m "Your commit message"```

---

### 3. Push to Remote

#### Push Your Branch to the Remote Repository:

```git push origin <your-branch-name>```

---

### 4. Create a Pull Request (PR) to Main

1. Navigate to the GitHub Repository in your web browser.

2. **Create a Pull Request:**
   - Go to the "Pull requests" tab.
   - Click on "New pull request".
   - Select your branch as the base branch and `main` as the compare branch.
   - Fill in the PR title and description with relevant information.
   - Click "Create pull request".

---

### 5. Review and Merge to Main

1. **Wait for Code Review:**
   - Your team members will review your PR.
   - Address any feedback or requested changes.

2. **Merge to Main:**
   - Once approved, merge your PR into the `main` branch.

---

#### Automatic Deployment:

- The GitHub Action will automatically deploy the changes once the PR is merged.
