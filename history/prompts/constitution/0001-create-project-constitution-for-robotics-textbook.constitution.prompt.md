---
id: 1
title: Create Project Constitution for Robotics Textbook
stage: constitution
date: 2025-12-10
surface: agent
model: gemini-pro
feature: none
branch: main
user: MuheebUrRehman
command: /sp.constitution
labels: ["constitution", "robotics", "docusaurus"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

/sp.constitution
Create a Project Constitution for a high-performance technical book:
Align strictly with the “Physical AI & Humanoid Robotics” course modules and learning outcomes.
Maintain academically reliable, technical writing using verified robotics sources and primary documentation.
Ensure consistent terminology across ROS 2, URDF/Xacro, controllers, Gazebo, Unity, Isaac Sim, Isaac ROS, Nav2, Whisper, and VLA systems.
Cite official robotics manuals, ROS REP standards, peer-reviewed papers, and vendor docs with precise references.
Provide clean examples, reproducible steps, and accurate system descriptions for every concept.
Exclude speculation, filler, non-verifiable statements, or untested workflows.
Use only the approved book-writing toolchain: Docusaurus v3.9.
Enforce a predictable chapter pattern:
Concept explanation → Diagram/code → Applied example → References.
Ensure diagrams and code samples follow real-world robotics conventions and compile/run where applicable.
Require accessibility: consistent formatting, glossary of robotics terms, and modular chapter independence.
Follow official Docusaurus documentation for structure, navigation, deployment, theming, and content organization.
Guarantee that every chapter can be generated independently while still conforming to the global constitution.
Each chapter will be at least 1000 words long.

## Response snapshot

I have created the project constitution in `.specify/memory/constitution.md` based on the principles you provided. The constitution is version 1.0.0. I also performed a consistency check of other project templates and found no issues.

## Outcome

- ✅ Impact: Established the foundational principles for the project in `.specify/memory/constitution.md`.
- 🧪 Tests: none
- 📁 Files: `.specify/memory/constitution.md`
- 🔁 Next prompts: none
- 🧠 Reflection: The provided principles were clear and detailed, allowing for a straightforward creation of the constitution document. The process of checking other templates for consistency is a good practice to ensure project coherence.

## Evaluation notes (flywheel)

- Failure modes observed: The PHR creation script mentioned in the instructions was not found. I had to fall back to the agent-native method of reading the template and creating the file.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Ensure the PHR creation script is available and executable in the environment.
