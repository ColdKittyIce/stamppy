---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---

name: Bug report
description: Something didn't work as expected
labels: [bug]
body:
  - type: textarea
    id: what-happened
    attributes:
      label: What happened?
      description: What did you expect vs. what actually happened?
      placeholder: "Expected X, saw Y..."
    validations: { required: true }
  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
      description: Be specific—include a small CSV snippet if possible (redact private info).
      placeholder: |
        1. Open Stamppy
        2. Load MicroSIP CSV
        3. Set UTC window 01:00–03:00
        4. Export Audacity labels
    validations: { required: true }
  - type: input
    id: version
    attributes:
      label: Stamppy version
      placeholder: "v0.1.0"
  - type: dropdown
    id: build-type
    attributes:
      label: Which build?
      options: ["Windows EXE (onefile)", "Windows ZIP (onedir)", "Source (Python)"]
  - type: textarea
    id: logs
    attributes:
      label: Error text / screenshots
