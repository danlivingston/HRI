Set-Location -Path "$PSScriptRoot\.."
echo "running isort..."
poetry run isort .
echo "running black..."
poetry run black .
echo "running flake8..."
poetry run flake8 .
echo "done"