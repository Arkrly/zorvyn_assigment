#!/bin/bash
# Render deployment build script

# Activate virtual environment
source venv/bin/activate

# Install dependencies using requirements.txt
pip install -r requirements.txt

# Run database migrations
alembic upgrade head