/* ************************************
maulal @ Alexis LACROIX
***************************************
usage:
mongo @uri --quiet restoreDocument.js

info:
This script, restore all backuped collection from wekan_archive database into the wekan database.

example:
mongo wekan --quiet restoreDocument.js
************************************ */

// restore function
// Move all backuped document into the original collection
function restoreOrphansCardData(orphansColName) {
    var orphansColBulk = db[orphansColName].initializeUnorderedBulkOp();
    var orphansCol = bk[orphansColName];
    print("---------------");
    print("Restore the collection: " + orphansColName);
    try {
        orphansCol.find().forEach(function(doc) {
            orphansColBulk.find({"_id": doc._id}).upsert().replaceOne(doc);
        });
        var orphansColBulkResult = orphansColBulk.tojson();
        orphansColBulk.execute();
        print("restore result: " + orphansColBulkResult);
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
    // list of archived collections
    var orphansDataCollectionsName = ["activities",
                                      "cards",
                                      "card_comments",
                                      "checklists",
                                      "cfs.attachments.filerecord",
                                      "cfs_gridfs.attachments.files",
                                      "cfs_gridfs.attachments.chunks",
                                      "cfs.avatars.filerecord",
                                      "cfs_gridfs.avatars.files",
                                      "cfs_gridfs.avatars.chunks",
                                      "lists"];
    // databases for the backup collection
    var bk = db.getSiblingDB("wekan_archive");

    orphansDataCollectionsName.forEach(function(col) {
        restoreOrphansCardData(col);
    });

} else {
    print("MongoDB need to be " + mongoVersion);
}