# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **autoscheduler2** project - a scheduling automation tool that is currently in its initial setup phase. The repository contains only documentation and setup notes, with no application code implemented yet.

## Development Environment

- **Platform**: WSL (Windows Subsystem for Linux) running Ubuntu
- **Runtime**: Python (all schedule management will be done in Python)
- **Database**: Neo4j graph database (planned, to be run via Docker)
- **AI Assistant**: Claude CLI for development assistance

## Setup Instructions

Based on the README.md, the development environment requires:

1. **Python**: Primary programming language for schedule management
2. **WSL/Ubuntu**: Linux environment on Windows
3. **Docker**: For containerization (Neo4j database)
4. **Claude CLI**: Available via `claude` command

## Key Commands

Since this is an empty project, standard commands are not yet established. When development begins, typical commands would include:

- `python -m venv venv` - Create virtual environment
- `source venv/bin/activate` - Activate virtual environment
- `pip install -r requirements.txt` - Install dependencies
- `python main.py` - Run the application (once configured)
- `pytest` - Run tests (once configured)
- `docker ps` - Check running containers
- `docker start <name>` - Start a container

## Architecture Notes

The project appears to be planned as a Python application with:
- **Backend**: Python for schedule management logic
- **Database**: Neo4j graph database
- **Deployment**: Docker containers
- **Development**: WSL environment

## Current State

This is a newly initialized repository with only setup documentation. The actual application architecture, build process, and testing framework have not yet been implemented.

## Next Development Steps

To make this repository functional, it needs:
1. `package.json` initialization
2. Source code directory structure
3. Core application files
4. Testing framework setup
5. Build and deployment configuration