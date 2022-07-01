REM Read .ver file and put in variable
FOR /F %%i IN (.ver) DO set VER=%%i

docker build -t ultimate_lunch_manager:%VER% .
