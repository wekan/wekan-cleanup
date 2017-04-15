# wekan-cleanup

Tools to clean up Mongodb database and delete archived cards / list / boards (after few months)

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
