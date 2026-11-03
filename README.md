Docker Productivity Launchpad

A hands-on DevOps and containerization project that i published on NextWork. This project focuses on building, containerizing, and running a personal productivity dashboard using Docker, Docker volumes, networking, and custom port configurations.

Project Page: https://nextwork.ai/projects/253bfd34-d9f6-4a6c-bc9f-1a6f1111a8ca

Project Overview

Starting the day often involves reopening the same links before work can begin, while tracking completed tasks can feel disjointed. This project solves that problem by packaging a personal productivity dashboard into a reusable container image via Docker.

The application features:

Daily Launchpad: Set a primary focus beside a configurable focus timer, keep pinned links accessible, and track recent focused minutes.

Persistent Data Storage: Saved states and notes persist even after container deletion and replacement through a named Docker volume.

Container-Name DNS & Networking: A private local network where temporary checker containers can communicate securely with the launchpad using custom DNS names.

Isolated Profiles: Run separate isolated Work and Study profiles from the same built image simultaneously, each utilizing its own custom port and independent volume.

Tech Stack & Prerequisites

Engine & Virtualization: Docker Desktop (WSL 2 backend on Windows 10/11)

IDE & Terminal: Visual Studio Code with integrated PowerShell

Frontend: HTML, CSS, JavaScript (served via a lightweight containerized server environment)

Project Structure

product-launchpad/
├── Dockerfile          # Instructions for building the container image
└── static/             # Frontend assets (HTML, CSS, JS dashboard UI)
    ├── index.html
    ├── style.css
    └── script.js


Setup & Usage

1. Build the Image

Build the container image locally from the project root directory:

docker build -t productivity-launchpad .


2. Run with Persistent Data

Run the container on port 8080 while attaching a named volume for persistent storage:

docker run -d -p 8080:80 --name my-launchpad -v launchpad-data:/data productivity-launchpad


Access the dashboard in your browser at http://localhost:8080.

Key Learnings

Containerization: Packaging an app and its runtime environment into a predictable, portable Docker image using a Dockerfile.

Data Persistence: Decoupling short-lived container layers from persistent application data using named volumes.

Docker Networking: Setting up container-to-container communication and custom DNS resolution to test services internally.