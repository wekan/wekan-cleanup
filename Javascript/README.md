# wekan tools #

**Javascript tools for wekan !**

Those tools have been created to solve inconsistencies (because sometimes shits happens :D) and "activities" collection size.
In a near future, i will include one script to <s>really archived "archived" wekan boards / lists / cards and all linked elements</s>.

Why javascript?

- no need to install anything else than ***mongo*** (the javascript shell given by MongoDB)
- just to be readable (and maintained) by wekan committers
- security naturally included by the mongo shell (no need to specify or modify anything inside the script)

All of those tools use the bulk method for better performance.
All of those tools can be launched on the same host than mongod, or not ;)
All of those tools are idempotent.

## tools ##

### requirements ###

- mongo shell version >= 3.2.x
- mongod database version >= 3.2.x
- a mongod user that can read/write into wekan database and can write into wekan_archive database (if authent enabled on mongod)
- launch those tools outside business hour

### removeOrphanDocument.js ###

This script removes all inconsistencies between collections from the wekan database (it can archive the result into wekan_archive database).

#### usage ####

~~~
mongo @uri --quiet --eval "var backup = [true|false]" removeOrphanDocument.js
~~~

#### example ####

Removes all inconsistencies from wekan database, and put them into wekan_archive database:
~~~
[mongodb@wekandb ~]$ mongo wekan --quiet --eval "var backup = true" removeOrphanDocument.js
---------------
Backup orphans from: lists based on: boards
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 4528, "nRemoveOps" : 0, "nBatches" : 5 }
---
Delete orphans from: lists based on: boards
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 4528, "nBatches" : 5 }
---------------
Backup orphans from: cards based on: boards
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---
Delete orphans from: cards based on: boards
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Backup orphans from: activities based on: boards
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 4528, "nRemoveOps" : 0, "nBatches" : 5 }
---
Delete orphans from: activities based on: boards
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 4528, "nBatches" : 5 }
---------------
Backup orphans from: cards based on: lists
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---
Delete orphans from: cards based on: lists
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Backup orphans from: activities based on: lists
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---
Delete orphans from: activities based on: lists
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Backup orphans from: card_comments based on: cards
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 125, "nRemoveOps" : 0, "nBatches" : 1 }
---
Delete orphans from: card_comments based on: cards
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 125, "nBatches" : 1 }
---------------
Backup orphans from: checklists based on: cards
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---
Delete orphans from: checklists based on: cards
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Backup orphans from: activities based on: cards
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---
Delete orphans from: activities based on: cards
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Backup orphans from: activities based on: users
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---
Delete orphans from: activities based on: users
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Backup orphans from: cfs_gridfs.attachments.chunks
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
Backup orphans from: cfs_gridfs.attachments.files
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 9, "nRemoveOps" : 0, "nBatches" : 1 }
Backup orphans from: cfs.attachments.filerecord
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 10, "nRemoveOps" : 0, "nBatches" : 1 }
---
Delete orphans from: cfs_gridfs.attachments.chunks
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
Delete orphans from: cfs_gridfs.attachments.files
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 9, "nBatches" : 1 }
Delete orphans from: cfs.attachments.filerecord
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 10, "nBatches" : 1 }
---------------
Backup orphans from: cfs_gridfs.avatars.chunks
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
Backup orphans from: cfs_gridfs.avatars.files
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
Backup orphans from: cfs.avatars.filerecord
Backup orphans result: { "nInsertOps" : 0, "nUpdateOps" : 1, "nRemoveOps" : 0, "nBatches" : 1 }
---
Delete orphans from: cfs_gridfs.avatars.chunks
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
Delete orphans from: cfs_gridfs.avatars.files
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
Delete orphans from: cfs.avatars.filerecord
Delete orphans result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 1, "nBatches" : 1 }
~~~

### archiveActivities.js ###

This script removes activities, older than a number of days, but keep at least a number of activities per board (it can archive activities into wekan_archive database).

#### usage ####

~~~
mongo @uri --eval "var backup = true; var removeActivitiesOlderThan = [nb of days to keep activities]; var minActivitiesPerBoard = [nb of activities to keep per board];" --quiet archiveActivities.js
~~~

#### example ####

Archive all activities older than 180 days into the wekan_archive database, but keep at least 30 activities per board:

~~~
[mongodb@wekandb ~]$ mongo --quiet wekan --eval "var backup = true; var removeActivitiesOlderThan = 180; var minActivitiesPerBoard = 30;" archiveActivities.js
77249
~~~

Now, a simple check:
~~~
[mongodb@wekandb ~]$ mongo wekan_archive
[P:wekan] wekandb@wekan_archive> db.activities.count()
77249
[P:wekan] wekandb@wekan_archive> use wekan
switched to db wekan
[P:wekan] wekandb@wekan> db.activities.count()
69709
~~~

### archiveArchivedDocument.js ###

This script really archived "archived" wekan boards / lists / cards and all linked elements.

**Work in Progress... Coming soon...**

### restoreDocument.js ###

This script, restore all backuped collection from wekan_archive database into the wekan database.

#### usage ####

~~~
mongo @uri --quiet restoreDocument.js
~~~

#### example ####

Restore all activities that have been previously archived:

~~~
[mongodb@wekandb ~]$ mongo wekan --quiet restoreDocument.js
---------------
Restore the collection: activities
restore result: {
        "nInsertOps" : 0,
        "nUpdateOps" : 77249,
        "nRemoveOps" : 0,
        "nBatches" : 78
}
---------------
Restore the collection: cards
restore result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Restore the collection: card_comments
restore result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Restore the collection: checklists
restore result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Restore the collection: cfs.attachments.filerecord
restore result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Restore the collection: cfs_gridfs.attachments.files
restore result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Restore the collection: cfs_gridfs.attachments.chunks
restore result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Restore the collection: cfs.avatars.filerecord
restore result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Restore the collection: cfs_gridfs.avatars.files
restore result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Restore the collection: cfs_gridfs.avatars.chunks
restore result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
---------------
Restore the collection: lists
restore result: { "nInsertOps" : 0, "nUpdateOps" : 0, "nRemoveOps" : 0, "nBatches" : 0 }
~~~

