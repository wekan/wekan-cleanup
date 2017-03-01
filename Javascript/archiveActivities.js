/* ************************************
maulal @ Alexis LACROIX
***************************************
usage:
mongo @uri --eval "var backup = true; var removeActivitiesOlderThan = [nb of days to keep activities]; var minActivitiesPerBoard = [nb of activities to keep per board];" --quiet archiveActivities.js

info:
This script removes activities, older than a number of days, but keep at least a number of activities per board (it can archive activities into wekan_archive database).
default value:
- backup = true
- removeActivitiesOlderThan = 365
- minActivitiesPerBoard = 100

example:
mongo wekan --quiet --eval "var backup = true; var removeActivitiesOlderThan = 180; var minActivitiesPerBoard = 10;" archiveActivities.js
************************************ */

function archiveActivities(backup, removeActivitiesOlderThan, minActivitiesPerBoard) {
    var count = 0;
    if (backup) {
        var archiveActivitiesBulk = bk["activities"].initializeUnorderedBulkOp();
    }
    var activities = db["activities"];
    var activitiesBulk = db["activities"].initializeUnorderedBulkOp();

    if (removeActivitiesOlderThan == 0) {
        var filterOlderThan = {};
    } else {
        var filterOlderThan = { "createdAt": { "$lt" : new Date(ISODate().getTime() - removeActivitiesOlderThan * 24 * 60 * 60 * 1000) } };
    }
    
    db.boards.find().forEach(function(doc) {
        var countActivities = activities.count({ "boardId": doc._id });
        if (countActivities > minActivitiesPerBoard) {
            filterOlderThan["boardId"] = doc._id;
            var countActivitiesOlderThan = activities.count(filterOlderThan);
            if (countActivitiesOlderThan > 0) {
                if (countActivities - countActivitiesOlderThan > minActivitiesPerBoard) {
                    activities.find(filterOlderThan).forEach(function(bck) {
                        if (backup) {
                            archiveActivitiesBulk.find({"_id": bck._id}).upsert().replaceOne(bck);
                        }
                        activitiesBulk.find({"_id": bck._id}).removeOne();
                        count += 1;
                    });
                } else {
                    activities.find(filterOlderThan).sort({"createdAt": 1}).limit(countActivities - minActivitiesPerBoard).forEach(function(del) {
                        if (backup) {
                            archiveActivitiesBulk.find({"_id": del._id}).upsert().replaceOne(del);
                        }
                        activitiesBulk.find({"_id": del._id}).removeOne();
                        count += 1;
                    });
                }
            }
        }
    });
    if (backup) {
        archiveActivitiesBulk.execute();
    }
    activitiesBulk.execute();
    return count;
}

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
    // defined a default value if not set
    if (typeof removeActivitiesOlderThan === "undefined") {
        var removeActivitiesOlderThan = 365;
    }

    // defined a default value if not set
    if (typeof minActivitiesPerBoard === "undefined") {
        var minActivitiesPerBoard = 100;
    }

    // If not defined backup will be done
    if (typeof backup === "undefined") {
       var backup = true;
    }

    // databases for the backup collection
    var bk = db.getSiblingDB("wekan_archive");

    print(archiveActivities(backup, removeActivitiesOlderThan, minActivitiesPerBoard));
} else {
    print("MongoDB need to be " + mongoVersion);
}