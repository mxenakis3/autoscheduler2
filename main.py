#!/usr/bin/env python3
"""
Autoscheduler2 - LLM-driven project management scheduling tool.

This is the main entry point for the autoscheduler2 application.
It initializes the CLI and starts the program.
"""

import sys
import subprocess
import time
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src" # __file__ contains path to current script, parent gets the directory containing __file__. We are appending the src folder to the path
sys.path.insert(0, str(src_path)) # make sure python looks at src folder first when importing modules

try:
    from autoscheduler.cli import main as cli_main
except ImportError as e:
    print(f"Error importing CLI module: {e}")
    print("Make sure you're running from the project root directory and have installed dependencies.")
    sys.exit(1)


def check_docker_containers():
    """Check if Docker containers are running and start them if needed."""
    try:
        # Check if docker-compose is available
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("Warning: docker-compose not found. Continuing without Docker services.")
            return False
            
        # Check container status
        print("Checking Docker containers...")
        result = subprocess.run(['docker-compose', 'ps', '--services', '--filter', 'status=running'],
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        
        running_services = result.stdout.strip().split('\n') if result.stdout.strip() else []
        required_services = ['neo4j', 'chromadb']
        
        # Check which services need to be started
        services_to_start = [s for s in required_services if s not in running_services]
        
        if services_to_start:
            print(f"Starting Docker services: {', '.join(services_to_start)}")
            # Start the containers
            result = subprocess.run(['docker-compose', 'up', '-d'] + services_to_start,
                                  capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode != 0:
                print(f"Warning: Failed to start Docker containers: {result.stderr}")
                return False
                
            # Wait for services to be ready
            print("Waiting for services to be ready...")
            time.sleep(10)  # Initial wait for containers to start
            max_wait = 60  # Maximum wait time
            elapsed = 10
            
            while elapsed < max_wait:
                time.sleep(5)
                elapsed += 5
                
                # Check if Neo4j is ready by checking container health status
                health_check = subprocess.run(
                    ['docker', 'inspect', '--format', '{{.State.Health.Status}}', 'autoscheduler-neo4j'],
                    capture_output=True, text=True
                )
                
                if health_check.returncode == 0 and health_check.stdout.strip() == 'healthy':
                    print("Services are ready!")
                    return True
                    
                print(f"Still waiting for services... ({elapsed}s/{max_wait}s)")
            
            print("Warning: Services may not be fully ready, but continuing anyway.")
            return True
        else:
            print("All required Docker services are already running.")
            return True
            
    except Exception as e:
        print(f"Warning: Error checking Docker containers: {e}")
        print("Continuing without Docker services.")
        return False


def main():
    """Main entry point for the autoscheduler2 application."""
    try:
        # Check and start Docker containers if needed
        check_docker_containers()
        
        # Continue with normal CLI startup
        cli_main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()