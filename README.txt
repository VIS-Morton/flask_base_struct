ySQL
- http://dev.mysql.com/downloads/
- MySql Workbench, GUI to operate admin  http://dev.mysql.com/downloads/workbench/
- set account and database as described in config.ini [Development]

Python
- version 2.7.11
- Under project folder, run pip install -r requirements.txt
- Run python app.py
- In browser, check http://localhost:8080/version

APIDoc
- Install apidoc, http://apidocjs.com/#install
- Run: apidoc -i . -o ./apidoc

Redis
- version 3.2.100
- http://redis.io/download
- set account and database as described in config.ini [Development]

MongoDB
- version 3.2.7
- https://www.mongodb.com/download-center?jmp=docs
add test user :
    use vds3;
    db.createUser({user: "root", pwd : "1qaz2wsx", roles: [{role: "readWrite", db: "vds3"}]},{w: 1, j:true, wtimeout: 20000})
import default data:
    mongoimport -d vds3 -c vtag_raw `file_path`

socketio
- version 1.4.8
- https://github.com/socketio/socket.io/blob/master/History.md
Git
- https://git-scm.com/downloads
