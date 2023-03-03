# wekan-cleanup

Tools to clean up Mongodb database and delete archived cards / list / boards (after few months)

Using Python3.

## Local Installation

Need to have below Python module : pymongo

    pip install pymongo

You need to have authentification setup on Mongo database and port opened (if docker) and create user :

    use admin
    db.createUser({user: "admin",pwd: "admin123",roles: [ "readWrite"]})

WekanCleanUp will manage below actions :

- Set in lowecase email of users in database (alert if duplicated email)
- Delete archived boards older that day_to_keep_board_arch
- Delete live boards (with no cards into) older than day_to_keep_board_nocard
- Removing from boards deleting users (if user deleted from database...)
- Delete archived lists older that day_to_keep_list_arch
- Delete archived cards older that day_to_keep_card_arch
- Delete all the orphans objects at the end (lists,cards,checklists,cards_comments,attachements,files,chunks,activities)

You need to update parameters before executing it

    # Parameters
    day_to_keep_board_arch = 30
    day_to_keep_list_arch = 30
    day_to_keep_card_arch = 60
    day_to_keep_board_nocard = 15
    mongo_user = 'admin'
    mongo_password = 'admin123'
    mongo_server = 'localhost'
    mongo_port = '27017'

## Docker Installation


1. Build Docker Image

Run the following command in the source root directory to build the docker image:
```
    docker build -t wekan-cleanup .
```

### With DB authentication


2. Create MongoDB User

You still need a MongoDB user with access to the wekan database. 
If MongoDB is running in a docker container you could enter the container via docker (e.g. `docker exec -it wekan-db mongo`) and create the user:
```
    use admin
    db.createUser({user: "admin",pwd: "admin123",roles: [ "readWrite"]})
```

3. Save the password as a file

Save the password as the content of a file on your computer, for example:
```
    echo "admin123" > .MONGO_PASSWORD
```

4. Run the docker container with your custom settings

Before you execute this command, please make sure that you have a backup of your MongoDB.

```
docker run \
    --rm \
    -v "$PWD/.MONGO_PASSWORD:/.MONGO_PASSWORD" \
    --env "MONGO_PASSWORD_PATH=/.MONGO_PASSWORD" \
    --env "MONGO_USER=admin" \
    --env "MONGO_SERVER=wekandb" \
    --env "MONGO_PORT=27017" \
    --env "MONGO_DATABASE=wekan" \
    --env "DAYS_TO_KEEP_BOARD_ARCHIVE=30" \
    --env "DAYS_TO_KEEP_LIST_ARCHIVE=30" \
    --env "DAYS_TO_KEEP_CARD_ARCHIVE=60" \
    --env "DAYS_TO_KEEP_CARD_NOCARD=15" \
    --network "wekan-mongodb_wekan-tier" \
    wekan-cleanup
```

### Without DB authentication
**NOT** recommended in production environments

2. Run the docker container with your custom settings

Before you execute this command, please make sure that you have a backup of your MongoDB.

```
docker run \
    --rm \
    --env "MONGO_USER_AUTHENTICATION=false" \
    --env "MONGO_SERVER=wekandb" \
    --env "MONGO_PORT=27017" \
    --env "MONGO_DATABASE=wekan" \
    --env "DAYS_TO_KEEP_BOARD_ARCHIVE=30" \
    --env "DAYS_TO_KEEP_LIST_ARCHIVE=30" \
    --env "DAYS_TO_KEEP_CARD_ARCHIVE=60" \
    --env "DAYS_TO_KEEP_CARD_NOCARD=15" \
    --network "wekan-mongodb_wekan-tier" \
    wekan-cleanup
```

Make sure the MongoDB is accessible
If the MongoDB is running in a docker container, you could either use its [network](https://docs.docker.com/engine/reference/run/#network-settings) or expose the MongoDB port, the former is recommended. The example above uses the default network from the Wekan's docker-compose setup.

## Other useful parameters

- `MONGO_DIRECT_CONNECTION`: Don't try to connect to all replica nodes. Useful when you enable MongoDB replicaset to take advantage from Oplog, but the replica has been configured with an unreachable address (for example, `localhost:27017`). See [pymongo docs](https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient)