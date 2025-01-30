# this is a flask application, using GCP
# this document has all the important point for the project
# Note don't make the project structure very complex, i want it to be easily readable
# use datastore as database
# use python 3.10
# Make it a microservice structure

# There will be 3 kinds of user -- admin, marker and driver
--> Marker is the person who will mark all the routes by moving on the track in a truck
opening the app location
--> After the marker has created the route, admin assigns the route to the drivers and 
drivers travel the route . (Route statuses are scheduled, active, completed)

--> Admin is the person who will be creating the route and assigning it to the marker
for marking and then driver to travel for deliveries
--> Admin can also create driver, marker and new admin users from the admin portal


There will be 2 application , 1. Admin Portal (Accessible only by admins)
                            2. Driver/Marker App which will be used for delivery or route marking

# Admin Portal Features
0. Note there will be a login page for the admin (No Registration with reset password feature)
1. A page where it can see all the active routes (those which are scheduled and active)
2. A page where it can see all the inactive routes
3. A page to create a new route (this will create a new route in the  backend with a unique id and assign the admin user as creator)
4. Then assign the created route to the marker for recoding the path
5. After the marker have completed the route recording, the admin should be able to see the route enabled for driver assignment
6. Note While assigning the route to driver admin might assign markers along with driver (Make marker also available for assignment)
7. Then there will be a Employees page, which will show 3 tabs each for drivers, markers and admin users.
8. From these tabs admin can create new user of any of the 3 type and edit users and delete it

# Marker/ Driver App Features

# Marker App Features
1. Login page with reset password
2. A page where Marker will be able to see the routes assigned to his name (Each tab for scheduled(assigned but not started), active(started), completed) routes
3. When marker is starting the route then we have to create an efficient api with proper
data structure to store all the movement of the marker on the path (assume the frontend will call the api 
after every 1 minutes with all the coordinates stored in that 1 minute)
4. Note that the marker can travel for days so the path data can be very big, so each path detail 
cannot be stored in a entity we need to find a mechanism which will store any size of data and also
cache it properly.
5. The marker on the journer will mark some checkpoint with details like location name, contact number, photo, remarks
6. With the check points the coordinates will also be coming.
7. Make the api in such a way that if frontend does not want to share all the coordinates and only wants
to share the coordinates of the check point then also it should be possible.
8. There should be an api which will provide all the path details for specific routes to the frontend.

# Driver App Features

1. Login page with reset password
2. A page where driver will be able to see the routes assigned to his name (Each tab for scheduled(assigned but not started), active(started), completed) routes
3. When driver is starting the route then we have to create an efficient api with proper
data structure to store all the movement of the marker on the path (assume the frontend will call the api 
after every 1 minutes with all the coordinates stored in that 1 minute)
4. Note that the driver can travel for days so the path data can be very big, so each path detail 
cannot be stored in a entity we need to find a mechanism which will store any size of data and also
cache it properly.
5. whenever the driver reached a checkpoint then frontend will send the checkpoint reached and we have to make it reached in the backend.
6. Checkpoint id will be coming whenever the driver reaches it.
7. Make the api in such a way that if frontend does not want to share all the coordinates and only wants
to share the coordinates of the check point then also it should be possible.
8. There should be an api which will provide all the path details for specific routes to the frontend.
9. Note once the route gets completed then it again comes in inactive route to the admin portal and admin can
assign it again to a new driver or the same driver with proper date and time



# Route structure
{
  "table_name": "Routes",
  "columns": [
    {
      "name": "routeid",
      "type": "String",
      "is_primary_key": true
    },
    {
      "name": "route_name",
      "type": "String"
    },
    {
      "name": "status",
      "type": "String",
      "values": [
        "scheduled",
        "active",
        "completed"
      ]
    },
    {
      "name": "adminid",
      "type": "String"
    },
    {
      "name": "markerid",
      "type": "String"
    },
    {
      "name": "created_at",
      "type": "Timestamp"
    },
    {
      "name": "updated_at",
      "type": "Timestamp"
    },
    {
      "name": "paths",
      "type": "List"
    },
    {
      "name": "checkpoints",
      "type": "List",
      "value": [
        {
          "id": "yyyymmddHHMMSS~{i}",
          "location_name": "",
          "contact": "",
          "photo": ""
        }
      ]
    }
  ]
}


# Markedroute
{
  "table_name": "MarkedRoute",
  "columns": [
    {
      "name": "routeid~markerid~<i>",
      "type": "String",
      "is_primary_key": true
    },
    {
      "name": "routeid",
      "type": "String"
    },
    {
      "name": "markerid",
      "type": "String"
    },
    {
      "name": "nextroutetime",
      "type": "Timestamp"
    },
    {
      "name": "coordinates",
      "type": "list",
      "value": [
        {
          "id": "yyyymmddHHMMSS~{i}",
          "lan": "",
          "lon": ""
        }
      ]
    }
  ]
}

# users
{
  "table_name": "Users",
  "columns": [
    {
      "name": "userid",
      "type": "String",
      "is_primary_key": true
    },
    {
      "name": "name",
      "type": "String"
    },
    {
      "name": "photo",
      "type": "String"
    },
    {
      "name": "role",
      "type": "string"
    },
    {
      "name": "password",
      "type": "string"
    }
  ]
}

# Driver Routes
{
  "routeid": "",
  "driverid": "",
  "created_at": "",
  "statushistory": [],
  "status": "",
  "travelled_path": ["key~0", "key~1"]
}

#DriverTravelledPath
{
  "key": "DriverRouteKey~0",
  "coordinates": [
    {
      "id": "yyyymmddHHMMSS~{i}",
      "lan": "",
      "lon": ""
    }
  ],
  "checkpoints_completed": ["checkpointid"]
}
# Google Maps API key