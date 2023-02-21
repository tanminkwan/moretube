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

- How to run docker with this image::
    # docker run -d \
    --name=moretube-app \
    -e DATABASE_URI='postgresql://more:1q2w3e4r!!@ecam.creamm2xnb34.us-east-1.rds.amazonaws.com:5432/more' \
    -e REDIS_URI='redis://tiffanie.xghtcu.ng.0001.use1.cache.amazonaws.com:6379' \
    -p 80:5000 \
    -v /home/ubuntu/moretube/static:/static \
    tanminkwan/moretube
    
That's it!!
