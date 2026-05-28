import src

print("START IMPORT")

app = src.create_app()

print("APP CREATED:", app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug = False)
    src.models.transaction_db.test_connection()
