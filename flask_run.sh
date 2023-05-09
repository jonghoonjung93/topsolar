export FLASK_APP=web.py
export FLASK_ENV=development
export FLASK_RUN_PORT=5200

cd /Users/jonghoon/DATA/coding/python/topsolar/

# foreground run
#python3 -m flask run --no-debugger --port 5200

# background run
nohup python3 -m flask run --no-debugger --port 5200 &

#python -m flask run --host=127.0.0.1 --port=5001
# nohup /usr/bin/python3.8 -m flask run --host=127.0.0.1 --port=5000 &
