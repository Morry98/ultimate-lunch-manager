VER=$(head -n 1 '.ver')

docker build -t ultimate_lunch_manager:$VER .
