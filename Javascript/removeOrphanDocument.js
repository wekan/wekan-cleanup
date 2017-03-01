/* ************************************
maulal @ Alexis LACROIX
***************************************
usage:
mongo @uri --quiet --eval "var backup = [true|false]" removeOrphanDocument.js

info:
This script removes all inconsitencies between collections from the wekan database (it can archive the result into wekan_archive database).
default value:
- backup = true

example:
mongo wekan --quiet --eval "var backup = true" removeOrphanDocument.js
************************************ */

// Function for backuping (if enabled), then deleting orphans document
function deleteOrphansCardData(parentName, parentKey, orphansColName, orphansColKey, backup) {
    if (backup) {
        var archiveColBulk = bk[orphansColName].initializeUnorderedBulkOp();
    }
    var orphansColBulk = db[orphansColName].initializeUnorderedBulkOp();
    var orphansCol = db[orphansColName];
    try {
        // Tricks to search only if the key exists
        var orphansColKeyExists = {};
        orphansColKeyExists[orphansColKey] = { "$exists": true };
        orphansCol.aggregate([
            {$match: orphansColKeyExists },
            {$lookup:{
                    from: parentName,
                    localField: orphansColKey,
                    foreignField: parentKey,
                    as: "docs"
            }},
            {$match:{ "docs": { $eq: [] } }}
        ]).forEach(function(doc) {
            delete doc.docs;
            if (backup) {
                archiveColBulk.find({"_id": doc._id}).upsert().replaceOne(doc);
            }
            orphansColBulk.find({"_id": doc._id}).removeOne();
        });
        var orphansColBulkResult = orphansColBulk.tojson();
        print("---------------");
        if (backup) {
            var archiveColBulkResult = archiveColBulk.tojson();
            print("Backup orphans from: " + orphansColName + " based on: " + parentName);
            archiveColBulk.execute();
            print("Backup orphans result: " + archiveColBulkResult);
            print("---");
        }
        print("Delete orphans from: " + orphansColName + " based on: " + parentName);
        orphansColBulk.execute();
        print("Delete orphans result: " + orphansColBulkResult);
    } catch(e) {
        print(e);
    }
};

// Function for backuping, then deleting orphans data
function deleteOrphansCardFile(parentName, parentKey, orphansColName, orphansColKey, backup) {
    // Convert the name of the gridfs collections
    // linked to the framework used
    var orphansFileName = orphansColName.split(".").splice(0,2).join("_gridfs.") + ".files";
    var orphansChunkName = orphansColName.split(".").splice(0,2).join("_gridfs.") + ".chunks";
    if (backup) {
        var archiveColBulk = bk[orphansColName].initializeUnorderedBulkOp();
        var archiveFileBulk = bk[orphansFileName].initializeUnorderedBulkOp();
        var archiveChunkBulk = bk[orphansChunkName].initializeUnorderedBulkOp();
    }
    var orphansCol = db[orphansColName];
    var orphansFile = db[orphansFileName];
    var orphansChunk = db[orphansChunkName];
    var orphansColBulk = db[orphansColName].initializeUnorderedBulkOp();
    var orphansFileBulk = db[orphansFileName].initializeUnorderedBulkOp();
    var orphansChunkBulk = db[orphansChunkName].initializeUnorderedBulkOp();
    try {
        orphansCol.aggregate([
            {$lookup:{
                    from: parentName,
                    localField: orphansColKey,
                    foreignField: parentKey,
                    as: "docs"
            }},
            {$match:{ "docs": { $eq: [] } }}
        ]).forEach(function(doc) {
            delete doc.docs;
            if (backup) {
                archiveColBulk.find({"_id": doc._id}).upsert().replaceOne(doc);
            }
            orphansColBulk.find({"_id": doc._id}).removeOne();
            if ("copies" in doc && "attachments" in doc.copies && "key" in doc.copies.attachments) {
                var file = orphansFile.findOne({"_id": ObjectId(doc.copies.attachments.key)});
                if (backup) {
                    archiveFileBulk.find({"_id": ObjectId(doc.copies.attachments.key)}).upsert().replaceOne(file);
                }
                orphansFileBulk.find({"_id": ObjectId(doc.copies.attachments.key)}).removeOne();
                orphansChunk.find({"file_id": file._id}).forEach(function(chunk) {
                    if (backup) {
                        archiveChunkBulk.find({"_id": chunk._id}).upsert().replaceOne(chunk);
                    }
                    orphansChunkBulk.find({"_id": chunk._id}).removeOne();
                });
            }
        });
        print("---------------");
        if (backup) {
            var archiveChunkBulkResult = archiveChunkBulk.tojson();
            var archiveFileBulkResult = archiveFileBulk.tojson();
            var archiveColBulkResult = archiveColBulk.tojson();

            print("Backup orphans from: " + orphansChunkName);
            archiveChunkBulk.execute();
            print("Backup orphans result: " + archiveChunkBulkResult);

            print("Backup orphans from: " + orphansFileName);
            archiveFileBulk.execute();
            print("Backup orphans result: " + archiveFileBulkResult);

            print("Backup orphans from: " + orphansColName);
            archiveColBulk.execute();
            print("Backup orphans result: " + archiveColBulkResult);
            print("---");
        }
        var orphansChunkBulkResult = orphansChunkBulk.tojson();
        var orphansFileBulkResult = orphansFileBulk.tojson();
        var orphansColBulkResult = orphansColBulk.tojson();

        print("Delete orphans from: " + orphansChunkName);
        orphansChunkBulk.execute();
        print("Delete orphans result: " + orphansChunkBulkResult);

        print("Delete orphans from: " + orphansFileName);
        orphansFileBulk.execute();
        print("Delete orphans result: " + orphansFileBulkResult);

        print("Delete orphans from: " + orphansColName);
        orphansColBulk.execute();
        print("Delete orphans result: " + orphansColBulkResult);
        
    } catch(e) {
        print(e);
    }
};

// Check the mongodb compatibility
function verAvailable(v) {
    var vOp = v.substring(0, 1);
    var vCheck = v.substring(1);

    var ver = db.version();
    var verConcat = ver.split(".").splice(0,2).join(".");
    switch(vOp) {
    case "<":
        if (verConcat <= vCheck) {
            return true;
        }
        break;
    case "=":
        if (verConcat == vCheck) {
            return true;
        }
        break;
    case ">":
        if (verConcat >= vCheck) {
            return true;
        }
        break;
    case "!":
        if (verConcat != vCheck) {
            return true;
        }
        break;
    default:
        print("This operator does not exists: " + vOp);
    }
    return false;
}

// Compatibility check:
mongoVersion = ">3.2";
//     First car   = operator              : "<" "=" ">" "!"
//     Second part = major mongodb version : "3.0" "3.2" "3.4"
if (verAvailable(mongoVersion)) {
    // The list of linked collections
    var orphansDataCollectionsName = [
        {"parent": { "collection" : "boards", "key": "_id" },
        "children": [
            { "collection" : "lists", "key": "boardId" },
            { "collection" : "cards", "key": "boardId" },
            { "collection" : "activities", "key": "boardId" },
        ]},
        {"parent": { "collection" : "lists", "key": "_id" },
        "children": [
            { "collection" : "cards", "key": "listId" },
            { "collection" : "activities", "key": "listId" },
        ]},
        {"parent": { "collection" : "cards", "key": "_id" },
        "children": [
            { "collection" : "card_comments", "key": "cardId" },
            { "collection" : "checklists", "key": "cardId" },
            { "collection" : "activities", "key": "cardId" },
        ]},
        {"parent": { "collection" : "users", "key": "_id" },
        "children": [
            { "collection" : "activities", "key": "userId" },
        ]},
    ];
    // gridFS collections
    var orphansFileCollectionsName = [
        {"parent": { "collection" : "cards", "key": "_id" },
        "children": [
            { "collection" : "cfs.attachments.filerecord", "key": "cardId" },
        ]},
        {"parent": { "collection" : "users", "key": "_id" },
        "children": [
            { "collection" : "cfs.avatars.filerecord", "key": "userId" },
        ]},
    ];
    // database for archive data
    var bk = db.getSiblingDB("wekan_archive");

    // If not defined backup will be done
    if (typeof backup === "undefined") {
       var backup = true;
    }

    // Manage the collection
    orphansDataCollectionsName.forEach(function(colToCheck) {
        var col = colToCheck.parent.collection;
        var key = colToCheck.parent.key;
        colToCheck.children.forEach(function(child) {
            deleteOrphansCardData(col, key, child.collection, child.key, backup);
        });
    });

    // Manage the gridFS collection
    orphansFileCollectionsName.forEach(function(colToCheck) {
        var col = colToCheck.parent.collection;
        var key = colToCheck.parent.key;
        colToCheck.children.forEach(function(child) {
            deleteOrphansCardFile(col, key, child.collection, child.key, backup);
        });
    });
} else {
    print("MongoDB need to be " + mongoVersion);
}

