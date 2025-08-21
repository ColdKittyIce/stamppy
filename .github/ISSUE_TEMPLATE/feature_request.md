---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: ''
assignees: ''

---

name: Feature request
description: Suggest an idea or improvement
labels: [enhancement]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem to solve
      placeholder: "Editing takes longer because..."
  - type: textarea
    id: proposal
    attributes:
      label: Proposed solution
      placeholder: "Add an option to..."
    validations: { required: true }
  - type: textarea
    id: details
    attributes:
      label: Details / mockups
      placeholder: "Buttons, labels, example CSV, etc."
