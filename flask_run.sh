export FLASK_APP=web.py
export FLASK_ENV=development

# foreground run
#python -m flask run
python -m flask run --host=127.0.0.1 --port=5001

# background run
# nohup /usr/bin/python3.8 -m flask run --host=127.0.0.1 --port=5000 &
