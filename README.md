# wekan-cleanup
Tools to clean up Mongodb database and delete archived cards / list / boards (after few months)

Need to have below Python module : pymongo

    pip install pymongo

You need to have authentification setup on Mongo database and port opened (if docker)

WekanCleanUp will delete as well Board with no cards

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
