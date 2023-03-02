#!/usr/bin/env python
#
# cleanup.py
#
# Simple tool that will clean MongoDb database for Wekan and delete "old" data
# Tool will check as well email case of users in database (lowercase)
#
# Author: Florent MONTHEL (fmonthel@flox-arts.net)
#

#! /usr/bin/python

import os
import pprint
import argparse
import datetime
from pymongo import MongoClient

def main() :
	
	# Parameters
	day_to_keep_board_arch = int(os.environ.get("DAYS_TO_KEEP_BOARD_ARCHIVE", "30"))
	day_to_keep_list_arch = int(os.environ.get("DAYS_TO_KEEP_LIST_ARCHIVE", "30"))
	day_to_keep_card_arch = int(os.environ.get("DAYS_TO_KEEP_CARD_ARCHIVE", "60"))
	day_to_keep_board_nocard = int(os.environ.get("DAYS_TO_KEEP_CARD_NOCARD", "30"))
	mongo_user = os.environ.get('MONGO_USER', "admin")
	mongo_server = os.environ.get('MONGO_SERVER', "localhost")
	mongo_port = os.environ.get('MONGO_PORT', "27017")
	mongo_database = os.environ.get('MONGO_DATABASE', "wekan")
	mongo_user_authentication = os.environ.get('MONGO_USER_AUTHENTICATION', "true")
	mongo_direct_connection = os.environ.get('MONGO_DIRECT_CONNECTION', "false").lower() == 'true'
	if mongo_user_authentication.lower() == 'true':
		mongo_password = ''
		if os.environ.get('MONGO_PASSWORD_PATH') is not None:
			with open(os.environ.get('MONGO_PASSWORD_PATH'), 'r') as file:
				mongo_password = file.read().strip()
		mongo_login = mongo_user + ':' + mongo_password + '@'
	else:
		mongo_login = ''
	
	# Variables
	time_start = datetime.datetime.now()
	time_clean_board_arch = time_start - datetime.timedelta(day_to_keep_board_arch)
	time_clean_list_arch = time_start - datetime.timedelta(day_to_keep_list_arch)
	time_clean_card_arch = time_start - datetime.timedelta(day_to_keep_card_arch)
	time_clean_board_nocard = time_start - datetime.timedelta(day_to_keep_board_nocard)
	
	# BDD
	mongo = MongoClient('mongodb://' + mongo_login + mongo_server + ':' + mongo_port + '/', directConnection=mongo_direct_connection)
	db = mongo[mongo_database]
	users = db['users']
	boards = db['boards']
	lists = db['lists']
	cards = db['cards']
	checklists = db['checklists']
	card_comments = db['card_comments']
	activities = db['activities']
	attachments = db['cfs.attachments.filerecord']
	attachment_files = db['cfs_gridfs.attachments.files']
	attachment_chunks = db['cfs_gridfs.attachments.chunks']
	
	# Check case of emails in database - Warning in case of not unique emails
	print("[USERS] Checking users emails compliance (lowercase)...")
	for user in users.find() :
		# Email with uppercase
		user_duplicate = False
		if user['emails'][0]['address'] != user['emails'][0]['address'].lower() :
			for user_email_duplicate in users.find({'emails.address' : user['emails'][0]['address'].lower()}) :
				user_duplicate = True
				print("[USER][ALERT] Duplicate email user for " + user['_id'] + " (" + user['emails'][0]['address'] + ") and " + user_email_duplicate['_id'] + " (" + user_email_duplicate['emails'][0]['address'] + ")")
			# We can update database
			if user_duplicate == False :
				print("[USER] Email of " + user['_id'] + " will be updated in database to use lowercase (" + user['emails'][0]['address'].lower() + ") - Updating in progress...")
				user['emails'][0]['address'] = user['emails'][0]['address'].lower()
				users.update({'_id':user["_id"]}, {"$set": user}, upsert=False)
	
	# Clean ALL archived boards (older than time_clean_board_arch)
	print("[BOARDS] Deleting " + str(boards.count_documents({'archived': True, 'modifiedAt': {'$lt': time_clean_board_arch}})) + " archived board(s)....")
	boards.delete_many({'archived': True, 'modifiedAt': {'$lt': time_clean_board_arch}})
	
	# Clean ALL live boards with no cards into
	print("[BOARDS] Checking boards with no card into....")
	for board in boards.find() :
		if cards.count_documents({"boardId": board['_id']}) == 0  and board['createdAt'] < time_clean_board_nocard :
			if board['type'] == 'template-container':
				print("Ignoring " + str(board['_id']) + " because it's a template board ")
			else :
				print("[BOARD] Deleting board " + str(board['_id']) + " (0 card into and created more than " + str(day_to_keep_board_nocard) + " day(s) ago)....")
				boards.delete_one({'_id': board['_id']})

	# Will update boards to remove deleted users
	print("[BOARDS] Checking deleted user into boards (userId not more in database)....")
	for board in boards.find() :
		k = 0
		for member in board["members"] :
			if users.count_documents({"_id": member['userId']}) == 0 :
				print("[BOARD] User " + member['userId'] + " need to be removed from board " + board["_id"] + " - Updating in progress...")
				del board["members"][k]
				boards.update({'_id':board["_id"]}, {"$set": board}, upsert=False)
			k = k + 1
	
	# Clean ALL archived list (older than time_clean_list_arch)
	print("[LISTS] Deleting " + str(lists.count_documents({'archived': True, 'modifiedAt': {'$lt': time_clean_list_arch}})) + " archived list(s)....")
	lists.delete_many({'archived': True, 'modifiedAt': {'$lt': time_clean_list_arch}})
	
	# Clean ALL archived cards (older than time_clean_card_arch)
	print("[CARDS] Deleting " + str(cards.count_documents({'archived': True, 'dateLastActivity': {'$lt': time_clean_card_arch}})) + " archived cards(s)....")
	cards.delete_many({'archived': True, 'dateLastActivity': {'$lt': time_clean_card_arch}})
	
	# Will update cards to remove deleted users
	print("[CARDS] Checking deleted user into cards (userId not more in database)....")
	for card in cards.find() :
		if 'members' in card :
			for member in card["members"] :
				if users.count_documents({"_id": member}) == 0 :
					print("[CARD] User " + member + " need to be removed from card " + card["_id"] + " - Updating in progress...")
					card["members"].remove(member)
					cards.update({'_id':card["_id"]}, {"$set": card}, upsert=False)
	
	# Will delete now lists with no boards
	print("[LISTS] Deleting " + str(lists.count_documents({'boardId': 'false'})) + " orphan list(s) (boardId = False)....")
	lists.delete_many({'boardId': 'false'})
	
	# Will delete lists with boardId not more in database
	print("[LISTS] Checking orphan lists (boardId not more in database)....")
	for list in lists.find() :
		# Get the board
		if boards.count_documents({"_id": list['boardId']}) == 0 :
			print("[LIST] Deleting orphan list " + str(list['_id']) + " (boardId not more in database)....")
			lists.delete_one({'_id': list['_id']})
	
	# Will delete cards with boardId or ListId or UserId not more in database
	print("[CARDS] Checking orphan cards (boardId or listId or userId not more in database)....")
	for card in cards.find() :
		# Get the board and list and user
		if boards.count_documents({"_id": card['boardId']}) == 0 or lists.count_documents({"_id": card['listId']}) == 0 or users.count_documents({"_id": card['userId']}) == 0 :
			print("[CARD] Deleting orphan card " + str(card['_id']) + " (boardId or listId or userId not more in database)....")
			cards.delete_one({'_id': card['_id']})
	
	# Will delete checklist with cardId not more in database
	print("[CHECKLISTS] Checking orphan checklist (cardId or userId not more in database)....")
	for checklist in checklists.find() :
		# Get the card
		if cards.count_documents({"_id": checklist['cardId']}) == 0 or 'userId' not in checklist.keys() or users.count_documents({"_id": checklist['userId']}) == 0 :
			print("[CHECKLIST] Deleting orphan checklist " + str(checklist['_id']) + " (cardId or userId not more in database)....")
			checklists.delete_one({'_id': checklist['_id']})

	# Will delete card_comments with cardId or userId more in database
	print("[CARD_COMMENTS] Checking orphan card_comments (cardId or userId not more in database)....")
	for card_comment in card_comments.find() :
		# Get the card and user
		if cards.count_documents({"_id": card_comment['cardId']}) == 0 or users.count_documents({"_id": card_comment['userId']}) == 0:
			print("[CARD_COMMENT] Deleting orphan card_comment " + str(card_comment['_id']) + " (cardId or userId not more in database)....")
			card_comments.delete_one({'_id': card_comment['_id']})
	
	# Will delete attachments with cardId or userId more in database
	print("[ATTACHMENTS] Checking orphan attachments (cardId or userId not more in database)....")
	for attachment in attachments.find() :
		# Get the card and user
		if cards.count_documents({"_id": attachment['cardId']}) == 0 or users.count_documents({"_id": attachment['userId']}) == 0 :
			print("[ATTACHEMENT] Deleting orphan attachment " + str(attachment['_id']) + " (cardId or userId not more in database)....")
			attachments.delete_one({'_id': attachment['_id']})
			

	# Will delete attachment_files with attachment more in database
	print("[ATTACHMENT_FILES] Checking orphan attachment files (attachment not more in database)....")
	for attachment_file in attachment_files.find() :
		# Get the attachment associated
		if attachments.count_documents({"copies.attachments.key" : str(attachment_file['_id'])}) == 0 :
			print("[ATTACHMENT_FILES] Deleting orphan attachment files " + str(attachment_file['_id']) + " (attachment not more in database)....")
			attachment_files.delete_one({'_id': attachment_file['_id']})
	
	# Will delete attachment_chunks with file_id more in database
	print("[ATTACHMENT_CHUNKS] Checking orphan attachment chunks (file_id not more in database)....")
	for attachment_chunk in attachment_chunks.find() :
		# Get the attachment associated
		if attachments.count_documents({"copies.attachments.key" : str(attachment_chunk['files_id'])}) == 0 :
			print("[ATTACHMENT_CHUNKS] Deleting orphan attachment chunks " + str(attachment_chunk['_id']) + " (file_id not more in database)....")
			attachment_chunks.delete_one({'_id': attachment_chunk['_id']})
	
	# Will delete activities
	print("[ACTIVITIES] Checking orphan activities (cardId or userId or boardId or listId or oldListId or commentId not more in database)....")
	for activity in activities.find() :
		# Get the card
		if 'cardId' in activity and cards.count_documents({"_id": activity['cardId']}) == 0 :
			print("[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (cardId not more in database)....")
			activities.delete_one({'_id': activity['_id']})
		elif 'userId' in activity and users.count_documents({"_id": activity['userId']}) == 0 :
			print("[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (userId not more in database)....")
			activities.delete_one({'_id': activity['_id']})
		elif 'boardId' in activity and boards.count_documents({"_id": activity['boardId']}) == 0 :
			print("[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (boardId not more in database)....")
			activities.delete_one({'_id': activity['_id']})
		elif 'listId' in activity and activity['listId'] is not None and lists.count_documents({"_id": activity['listId']}) == 0 :
			print("[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (listId not more in database)....")
			activities.delete_one({'_id': activity['_id']})
		elif 'oldListId' in activity and lists.count_documents({"_id": activity['oldListId']}) == 0 :
			print("[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (oldListId not more in database)....")
			activities.delete_one({'_id': activity['_id']})
		elif 'checklistId' in activity and checklists.count_documents({"_id": activity['checklistId']}) == 0 :
			print("[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (checklistId not more in database)....")
			activities.delete_one({'_id': activity['_id']})
		elif 'attachmentId' in activity and attachments.count_documents({"_id": activity['attachmentId']}) == 0 :
			print("[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (attachmentId not more in database)....")
			activities.delete_one({'_id': activity['_id']})
		elif 'commentId' in activity and card_comments.count_documents({"_id": activity['commentId']}) == 0 :
			print("[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (commentId not more in database)....")
			activities.delete_one({'_id': activity['_id']})

if __name__ == "__main__" :
	main()
