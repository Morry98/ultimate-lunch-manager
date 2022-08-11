
echo "Installing dependencies"
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo "Auto formatting code with black"
black ultimate_lunch_manager main.py

echo "Run linting"
flake8 ultimate_lunch_manager main.py || goto :error

echo "Run type checking"
mypy --install-types --non-interactive ultimate_lunch_manager main.py || goto :error

echo "Running tests"
coverage run --source=ultimate_lunch_manager -m pytest || goto :error
ECHO "Create HTML Coverage report"
coverage html || goto :error
ECHO "Coverage report"
coverage report --show-missing --skip-covered --skip-empty --omit="*test*,*exception*" || goto :error
goto :end

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%

:end
echo Pipeline run succesfully
