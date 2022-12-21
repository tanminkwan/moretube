Base Skeleton to start your application using Flask-AppBuilder
--------------------------------------------------------------

- Install it::

	pip install flask-appbuilder
	git clone https://github.com/dpgaspar/Flask-AppBuilder-Skeleton.git

- Run it::

    $ export FLASK_APP=app
    # Create an admin user
    $ flask fab create-admin
    # Run dev server
    $ flask run

- Migrate DB Models::

    # Alembic을 처음 실행
    $ flask db init
    # db migration code 생성
    $ flask db migrate
    # db migration code 실행
    $ flask db upgrade

- Favicon Setting::

    # favicon 파일 저장
    app/static/ 에 favicon.ico 파일 저장
    # flask_appbuilder 원본 수정
    대상파일 : 
    flask_appbuilder/templates/appbuilder/init.html
    head tag 안에 code 추가 : 
    <link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='favicon.ico') }}">

That's it!!
