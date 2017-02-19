#!/usr/bin/env python
#
# cleanup.py
#
# Simple tool that will clean MongoDb database for Wekan and delete "old" data
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
	day_to_keep_board_arch = 30
	day_to_keep_list_arch = 30
	day_to_keep_card_arch = 60
	day_to_keep_board_nocard = 15
	mongo_user = 'admin'
	mongo_password = 'admin123'
	mongo_server = 'localhost'
	mongo_port = '27017'
	
	# Variables
	time_start = datetime.datetime.now()
	time_clean_board_arch = time_start - datetime.timedelta(day_to_keep_board_arch)
	time_clean_list_arch = time_start - datetime.timedelta(day_to_keep_list_arch)
	time_clean_card_arch = time_start - datetime.timedelta(day_to_keep_card_arch)
	time_clean_board_nocard = time_start - datetime.timedelta(day_to_keep_board_nocard)
	
	# BDD
	mongo = MongoClient('mongodb://' + mongo_user + ':' + mongo_password + '@' + mongo_server + ':' + mongo_port + '/')
	db = mongo['admin']
	users = db['users']
	boards = db['boards']
	lists = db['lists']
	cards = db['cards']
	checklists = db['checklists']
	card_comments = db['card_comments']
	activities = db['activities']
	attachments = db['cfs.attachments.filerecord']
	
	# Clean ALL archived boards (older than time_clean_board_arch)
	print "[BOARDS] Deleting " + str(boards.count({'archived': True, 'modifiedAt': {'$lt': time_clean_board_arch}})) + " archived board(s)...."
	boards.delete_many({'archived': True, 'modifiedAt': {'$lt': time_clean_board_arch}})
	
	# Clean ALL live boards with no cards into
	print "[BOARDS] Checking boards with no card into...."
	for board in boards.find() :
		if cards.count({"boardId": board['_id']}) == 0  and board['createdAt'] < time_clean_board_nocard :
			print "[BOARD] Deleting board " + str(board['_id']) + " (0 card into and created more than " + str(day_to_keep_board_nocard) + " day(s) ago)...."
			boards.delete_one({'_id': board['_id']})
	
	# Will update boards to remove deleted users
	print "[BOARDS] Checking deleted user into boards (userId not more in database)...."
	for board in boards.find() :
		k = 0
		for member in board["members"] :
			if users.count({"_id": member['userId']}) == 0 :
				print "[BOARD] User " + member['userId'] + " need to be removed from board " + board["_id"] + " - Updating in progress..."
				del board["members"][k]
				boards.update({'_id':board["_id"]}, {"$set": board}, upsert=False)
			k = k + 1
	
	# Clean ALL archived list (older than time_clean_list_arch)
	print "[LISTS] Deleting " + str(lists.count({'archived': True, 'modifiedAt': {'$lt': time_clean_list_arch}})) + " archived list(s)...."
	lists.delete_many({'archived': True, 'modifiedAt': {'$lt': time_clean_list_arch}})
	
	# Clean ALL archived cards (older than time_clean_card_arch)
	print "[CARDS] Deleting " + str(cards.count({'archived': True, 'dateLastActivity': {'$lt': time_clean_card_arch}})) + " archived cards(s)...."
	cards.delete_many({'archived': True, 'dateLastActivity': {'$lt': time_clean_card_arch}})
	
	# Will update cards to remove deleted users
	print "[CARDS] Checking deleted user into cards (userId not more in database)...."
	for card in cards.find() :
		if 'members' in card :
			for member in card["members"] :
				if users.count({"_id": member}) == 0 :
					print "[CARD] User " + member + " need to be removed from card " + card["_id"] + " - Updating in progress..."
					card["members"].remove(member)
					cards.update({'_id':card["_id"]}, {"$set": card}, upsert=False)
	
	# Will delete now lists with no boards
	print "[LISTS] Deleting " + str(lists.count({'boardId': 'false'})) + " orphan list(s) (boardId = False)...."
	lists.delete_many({'boardId': 'false'})
	
	# Will delete lists with boardId not more in database
	print "[LISTS] Checking orphan lists (boardId not more in database)...."
	for list in lists.find() :
		# Get the board
		if boards.count({"_id": list['boardId']}) == 0 :
			print "[LIST] Deleting orphan list " + str(list['_id']) + " (boardId not more in database)...."
			lists.delete_one({'_id': list['_id']})
	
	# Will delete cards with boardId or ListId or UserId not more in database
	print "[CARDS] Checking orphan cards (boardId or listId or userId not more in database)...."
	for card in cards.find() :
		# Get the board and list and user
		if boards.count({"_id": card['boardId']}) == 0 or lists.count({"_id": card['listId']}) == 0 or users.count({"_id": card['userId']}) == 0 :
			print "[CARD] Deleting orphan card " + str(card['_id']) + " (boardId or listId or userId not more in database)...."
			cards.delete_one({'_id': card['_id']})
	
	# Will delete checklist with cardId not more in database
	print "[CHECKLISTS] Checking orphan checklist (cardId or userId not more in database)...."
	for checklist in checklists.find() :
		# Get the card
		if cards.count({"_id": checklist['cardId']}) == 0 or users.count({"_id": checklist['userId']}) == 0 :
			print "[CHECKLIST] Deleting orphan checklist " + str(checklist['_id']) + " (cardId or userId not more in database)...."
			checklists.delete_one({'_id': checklist['_id']})

	# Will delete card_comments with cardId or userId more in database
	print "[CARD_COMMENTS] Checking orphan card_comments (cardId or userId not more in database)...."
	for card_comment in card_comments.find() :
		# Get the card and user
		if cards.count({"_id": card_comment['cardId']}) == 0 or users.count({"_id": card_comment['userId']}) == 0:
			print "[CARD_COMMENT] Deleting orphan card_comment " + str(card_comment['_id']) + " (cardId or userId not more in database)...."
			card_comments.delete_one({'_id': card_comment['_id']})
	
	# Will delete attachments with cardId or userId more in database
	print "[ATTACHEMENTS] Checking orphan attachments (cardId or userId not more in database)...."
	for attachment in attachments.find() :
		# Get the card and user
		if cards.count({"_id": attachment['cardId']}) == 0 or users.count({"_id": attachment['userId']}) == 0:
			print "[ATTACHEMENT] Deleting orphan attachment " + str(attachment['_id']) + " (cardId or userId not more in database)...."
			attachments.delete_one({'_id': attachment['_id']})
	
	# Will delete activities
	print "[ACTIVITIES] Checking orphan activities (cardId or userId or boardId or listId or oldListId or commentId not more in database)...."
	for activity in activities.find() :
		# Get the card
		if 'cardId' in activity and cards.count({"_id": activity['cardId']}) == 0 :
			print "[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (cardId not more in database)...."
			activities.delete_one({'_id': activity['_id']})
		elif 'userId' in activity and users.count({"_id": activity['userId']}) == 0 :
			print "[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (userId not more in database)...."
			activities.delete_one({'_id': activity['_id']})
		elif 'boardId' in activity and boards.count({"_id": activity['boardId']}) == 0 :
			print "[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (boardId not more in database)...."
			activities.delete_one({'_id': activity['_id']})
		elif 'listId' in activity and lists.count({"_id": activity['listId']}) == 0 :
			print "[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (listId not more in database)...."
			activities.delete_one({'_id': activity['_id']})
		elif 'oldListId' in activity and lists.count({"_id": activity['oldListId']}) == 0 :
			print "[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (oldListId not more in database)...."
			activities.delete_one({'_id': activity['_id']})
		elif 'checklistId' in activity and checklists.count({"_id": activity['checklistId']}) == 0 :
			print "[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (checklistId not more in database)...."
			activities.delete_one({'_id': activity['_id']})
		elif 'attachmentId' in activity and attachments.count({"_id": activity['attachmentId']}) == 0 :
			print "[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (attachmentId not more in database)...."
			activities.delete_one({'_id': activity['_id']})
		elif 'commentId' in activity and card_comments.count({"_id": activity['commentId']}) == 0 :
			print "[ACTIVITY] Deleting orphan activity " + str(activity['_id']) + " (commentId not more in database)...."
			activities.delete_one({'_id': activity['_id']})

if __name__ == "__main__" :
	main()