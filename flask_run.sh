export FLASK_APP=web.py
export FLASK_ENV=development
export FLASK_RUN_PORT=5200

# foreground run
nohup python3 -m flask run --no-debugger &
#python -m flask run --host=127.0.0.1 --port=5001

# background run
# nohup /usr/bin/python3.8 -m flask run --host=127.0.0.1 --port=5000 &
