CALL .\server\env\Scripts\activate
flask --app .\server\app.py:create_app run | npm --prefix .\client\ run dev