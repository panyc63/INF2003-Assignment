# run.py (in your root INF2003-Assignment folder)
from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)