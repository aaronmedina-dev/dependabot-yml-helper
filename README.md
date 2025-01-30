# 🚀 dependabot-yml-helper

Aaron Medina | [GitHub](https://github.com/aaronmedina-dev) | [Linkedin](https://www.linkedin.com/in/aamedina/)

A **helper tool** for generating **base dependabot.yml files** and providing **dependency patterns** for better insights on how to optimise groups and other configuration.

---

## **Why use this?**
Writing a **dependabot.yml** file can be tricky since there are many ways to structure it. **This tool does not attempt to create the "best" dependabot.yml file** because:
- There are multiple ways to group PRs (by ecosystem, by folder, by dependency type, etc.).
- Different projects have **different update strategies** and PR handling methods.


Instead, this helper:

✅ **Generates a base dependabot.yml file**  
✅ **Lists all detected package ecosystems** in your project  
✅ **Provides folder and dependency patterns** for better insights  

---

## **Requirements**
- Python 3.7 or higher
- Install **PyYAML**:
  ```bash
  pip install pyyaml
  ```

---

## **Usage**
### **🔹 Generate `dependabot.yml`**
```bash
python generate_dependabot.py
```
This will create a **base `dependabot.yml` file** inside the `OUTPUT/` folder.

---

### **🔹 Generate `package-ecosystem-patterns.yml`**
```bash
python generate_patterns.py
```
This will create **`package-ecosystem-patterns.yml`** inside the `OUTPUT/` folder, listing:
- **Folder patterns** → Actual directories where dependencies were found.
- **Dependency patterns** → Extracted dependencies from `package.json`, `requirements.txt`, etc.

---

## **Example Outputs**
### **Generated `dependabot.yml`**
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    target-branch: "main"

  - package-ecosystem: "github-actions"
    directory: "/.github/workflows"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    target-branch: "main"
```

---

### **Generated `package-ecosystem-patterns.yml`**
```yaml
pattern-list:
- package-ecosystem: "npm"
  folder-patterns:
    - "/."
    - "/packages/basic-auth"
    - "/packages/cloudfront-security-headers"
  dependency-patterns:
    - "aws-sdk"
    - "express"
    - "prerender"

- package-ecosystem: "github-actions"
  folder-patterns:
    - "/.github/workflows"
  dependency-patterns: []
```

---

## **Customizing `dependabot.yml`**
Once the **base file** is generated, you can **customize it further**:
### **1️⃣ Group dependencies**
Modify `dependabot.yml` to **group PRs**:
```yaml
groups:
  aws:
    patterns:
      - "aws-sdk*"
      - "@aws-sdk*"
  ui-frameworks:
    patterns:
      - "react"
      - "vue"
      - "angular"
```

### **2️⃣ Adjust update intervals**
Modify how often each ecosystem checks for updates:
```yaml
schedule:
  interval: "weekly"  # Change to "daily" or "monthly" as needed
```

---

## **Configuration**
Edit `user_config.yaml` to modify settings:
```yaml
settings:
  base_path: "/your-project-path"
  branch: "main"
  intervals:
    pip: "daily"
    npm: "weekly"
    docker: "monthly"
  pull_requests_limit: 10
  ignored_paths:
    - "**/node_modules/**"
    - dist
    - build
    - .git
  grouping_strategy: "none"  # Options: "none", "package-ecosystem", "custom"
  custom_groups:
    - name: "core-packages"
      directories:
        - "../your-project"
        - "../your-project/packages/shared-vpc"
```

---

## **How This Helps You**
📌 **Quickly generate a solid base `dependabot.yml` file**  
📌 **Automatically detect package ecosystems & dependencies**  
📌 **Get insights into how PRs can be grouped optimally**  
📌 **Ensure that ignored paths (e.g., `node_modules`) are excluded**  

💡 **Instead of trying to write the "best" dependabot.yml file, this tool helps you create an informed, customizable starting point!**

---

## **Contributing**
Feel free to:
- **Submit PRs** if you have ideas to improve automation.
- **Report issues** if you encounter bugs.
- **Fork the repo** and add more ecosystem support.

---

## **License**
This project is licensed under the **MIT License**.

