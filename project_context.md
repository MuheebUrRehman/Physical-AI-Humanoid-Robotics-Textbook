# Project: Physical AI & Humanoid Robotics Textbook

## Goal

Build a Docusaurus-based textbook on Physical AI & Humanoid Robotics, deployed to vercel, with an embedded RAG chatbot and optional bonus features.

## Tech Stack

- **Book**: Docusaurus, deployed to Vercel
- **RAG Chatbot**: OpenAI Agents SDK / ChatKit SDK, FastAPI, Neon Serverless Postgres, Qdrant Cloud (free tier)
- **Auth (bonus)**: [better-auth](https://www.better-auth.com/)
- **Tooling**: opencode + [Spec-Kit Plus](https://github.com/panaversity/spec-kit-plus/)

## Deliverables

1. **Docusaurus book** — full textbook content (see course outline below), deployed publicly
2. **RAG chatbot** — embedded in the book; answers questions about book content, including questions based on user-selected text
3. **Bonus — Auth**: Signup/signin via better-auth; collect user's software/hardware background at signup for personalization
4. **Bonus — Personalization**: Logged-in users can press a button at the start of each chapter to personalize content to their background
5. **Bonus — Urdu translation**: Logged-in users can press a button at the start of each chapter to translate content to Urdu
6. **Bonus — opencode Subagents/Skills**: Use reusable opencode subagents and agent skills throughout the build

## Course Outline (Textbook Content)

### Module 1: The Robotic Nervous System (ROS 2)

- ROS 2 nodes, topics, services
- Bridging Python agents to ROS controllers via `rclpy`
- URDF (Unified Robot Description Format) for humanoids

### Module 2: The Digital Twin (Gazebo & Unity)

- Physics simulation (gravity, collisions) in Gazebo
- High-fidelity rendering and human-robot interaction in Unity
- Sensor simulation: LiDAR, Depth Cameras, IMUs

### Module 3: The AI-Robot Brain (NVIDIA Isaac)

- NVIDIA Isaac Sim: photorealistic simulation, synthetic data generation
- Isaac ROS: hardware-accelerated VSLAM and navigation
- Nav2: path planning for bipedal humanoid movement

### Module 4: Vision-Language-Action (VLA)

- Voice-to-Action: OpenAI Whisper for voice commands
- LLM-driven cognitive planning: natural language → ROS 2 action sequences
- Capstone: simulated robot receives voice command, plans path, navigates obstacles, identifies and manipulates object via computer vision

