from app import create_app

#app imported from app/__init__.py

app = create_app()

#app entry point

if __name__ == "__main__":
    app.run(debug=True)