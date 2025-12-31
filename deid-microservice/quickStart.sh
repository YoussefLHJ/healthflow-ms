# Script: run_healthflow.sh
# Description: Entry point script for the HealthFlow microservices application
# Shebang: #!/bin/bash - Specifies that this script should be executed using the Bash shell
# Usage: ./run_healthflow.sh

#!/bin/bash
# Open a new terminal window and run the deid-microservice

# Then remove or comment out the lines below since they'll run in the new terminal:
source .venv/Scripts/activate
uvicorn deid_service:app --host 0.0.0.0 --port 8000 --reload


