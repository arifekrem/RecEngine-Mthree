import src

if __name__ == "__main__":
    app = src.create_app()
    app.run(host="0.0.0.0", debug = False)
    # src.models.transaction_db.test_connection()
