## EventHub RESTful API

### HOW TO SETUP
```
git clone http://github.com/rajmani1995/EventHub-API.git

pip install -r requirements.txt

python app.py

```
### To Manage migrations

```
# point to current application
export FLASK_APP=app.py
flask db init
# to create a new migration
flask db migrate
# to upgrade database
flask db upgrade
```
server started on http://127.0.0.1:5000

```
ROOT_URL = http://127.0.0.1:5000/api/v1
```

### HOW TO

#### To create a new user (First user is always Admin)

Admin can make other user as admin

```
$ curl -i -X POST -H "Content-Type:application/json" http://localhost:5000/api/v1/users -d '{"username": "rest_user","first_name": "Rest","password":"s3cr3t","email":"restuser@gmail.com","last_name":"User","phone":"9000012345"}'

HTTP/1.0 201 CREATED
Content-Type: application/json
Location: http://localhost:5000/api/v1/users/1
Content-Length: 28
Server: Werkzeug/0.11.11 Python/2.7.12
Date: Sat, 17 Sep 2016 08:10:46 GMT

{
  "username": "rest_user"
}
```

#### Make other user admin

```
# Make admin of user whose _id=2
$ curl -u rest_user:s3cr3t -i -X PUT http://localhost:5000/api/v1/admin/2

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 102
Server: Werkzeug/0.11.11 Python/2.7.12
Date: Sat, 17 Sep 2016 08:10:02 GMT

{
  'status':"success",
  "message":"new admin created"
}

```

#### To get list of all user
```
$ curl -u rest_user:s3cr3t -X GET http://localhost:5000/api/v1/users

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 102
Server: Werkzeug/0.11.11 Python/2.7.12
Date: Sat, 17 Sep 2016 08:10:02 GMT

{
  "count": 1, 
  "status": "success", 
  "users": [
    {
      "_id": 1,
      "email": "restuser@gmail.com", 
      "full_name": "Rest User",
      "phone": "9000012345"
    }
  ]
}
```
#### To get a particular user
```
$ curl -u rest_user:s3cr3t -X GET  http://localhost:5000/api/v1/users/1

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 71
Server: Werkzeug/0.11.11 Python/2.7.12
Date: Sat, 17 Sep 2016 08:20:51 GMT

{
  "email": "restuser@gmail.com", 
  "full_name": "Rest User"
  "phone": "9000012345"
}

```
#### One time feedback submit

```
$ curl -u rest_user:s3cr3t -i -X POST -H "Content-Type:application/json" http://localhost:5000/api/v1/feedback -d '{"stars":"1", "comment":"Noce Job !"}'

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 64
Server: Werkzeug/0.11.11 Python/2.7.12
Date: Sat, 17 Sep 2016 08:27:33 GMT

{
  "message": "Feedback Submitted !", 
  "status": "success"
}


```

#### To Add an Event (Must be an administrator)

```
$ curl -u rest_user:s3cr3t -i -X POST -H "Content-Type:application/json" http://localhost:5000/api/v1/events -d '{"title":"Audi Night", "location":"Auditorium", "schedule":"2016-09-15 20:00:00", "requirements":"", "refreshment":0, "contact":"9000012345", "contact_alt":"", "logo_url":"http://localhost:5000/assets/audi_bight.png"}'

HTTP/1.0 201 CREATED
Content-Type: application/json
Location: http://localhost:5000/api/v1/events/1
Content-Length: 28
Server: Werkzeug/0.11.11 Python/2.7.12
Date: Sat, 17 Sep 2016 08:10:46 GMT

{
  "title": "Audi Night"
}
```

#### To get list of all events
```
# when {0,1,2} , 0 -> past events, 1->today events and 2 -> upcoming events

$ curl -u rest_user:s3cr3t -i -X GET http://localhost:5000/api/v1/events?when=0

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 318
Server: Werkzeug/0.11.11 Python/2.7.12
Date: Sat, 17 Sep 2016 08:31:35 GMT

{
  "events": [
    {
      "_id": 1,
      "contact": "9000012345", 
	    "contact_alt": "9000012345", 
      "location": "Stadium", 
      "logo_url": "/assets/ganesh_pooja.png", 
      "requirements": "", 
      "schedule": "Thu, 08 Sep 2016 20:00:00 GMT", 
      "title": "Ganesh Pooja"
    }
  ], 
  
  "status": "success"
}

```

#### To get a particular event

```
$ curl -u rest_user:s3cr3t -i -X GET http://localhost:5000/api/v1/events/1

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 295
Server: Werkzeug/0.11.11 Python/2.7.12
Date: Sat, 17 Sep 2016 08:31:11 GMT

{
  "event": {
    "_id": 2,
    "contact": "9000012345", 
    "contact_alt": "9000012345", 
    "location": "NIT Warangal", 
    "logo_url": "/assets/hackathon.png", 
    "requirements": "Laptop", 
    "schedule": "Sun, 18 Sep 2016 20:00:00 GMT", 
    "title": "Hackathon"
  }, 
  "status": "success"
}

```

#### To join an Event

```
$ curl -u rest_user:s3cr3t -i -X POST http://localhost:5000/api/v1/join/1

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 110
Server: Werkzeug/0.11.11 Python/2.7.12
Date: Sat, 17 Sep 2016 08:31:11 GMT

{
  "status":"success",
  "message":"Successfully Joined"
}
```
#### To get users going for a event

```
$ curl -u rest_user:s3cr3t -i -X POST http://localhost:5000/api/v1/going/1

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 110
Server: Werkzeug/0.11.11 Python/2.7.12
Date: Sat, 17 Sep 2016 08:31:11 GMT

{
  "status":"success",
  "count": 1,
  "users": [
    "Rajmani Arya"
  ]
}
```

### More updates coming soon