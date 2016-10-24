var env = process.env.NODE_ENV = process.env.NODE_ENV || 'development';
var config = require('../config/config')[env];
var Apk = require('mongoose').model('Apk');
var shell = require('shelljs');
var PythonShell = require('python-shell');
var fsExists = require('fs-exists');
const exec = require('child_process').exec;
const fs = require('fs');

exports.getAllApps = function (req, res) {
    Apk.find({}).exec(function (err, collection) {
        res.send(collection);
    })
};

exports.getAppsByUserName = function (req, res) {
    var curentUserName = req.user.username;
    Apk.find({username: curentUserName}).exec(function (err, collection) {
        var result = [];
        //console.log(collection.length);
        for (var i in collection) {
            var resultObj = {
                _id: collection[i]._id,
                title: collection[i].title,
                uploaded_on: collection[i].uploaded_on,
                isSA_done: collection[i].isSA_done,
                isSIG_done: collection[i].isSIG_done
            };
            result.push(resultObj);
        }
        //console.log(result);
        res.send(result);
    });
};

/*exports.getAppsById = function(req, res) {
 Apk.findOne({_id:req.params.id}).exec(function(err, app) {
 res.send(app);
 });
 }*/

exports.startTrigger = function (req, res) {
    trigerFileProcessing(req.body.file_id);
    res.json({error_code: 200, err_desc: "Trigger Started Successfully."});
};

exports.getSAReport = function (req, res) {
    Apk.findOne({_id: req.params._id}).exec(function (err, appData) {
        if (err) {
            res.status(400);
            return res.send({reason: err.toString()});
        }
        var report = JSON.parse(appData.SA_report);
        var is_vulnerable = report["is_velnerable"];
        var vulnerable = "NOT VULNERABLE";
        if (is_vulnerable) {
            vulnerable = "VULNERABLE";
        }
        var trust_manager = report["trust_manager"];
        var seeds = report["seeds"];
        var v_end_points = report["v_end_points"];
        var apk_package = report["apk_package"];
        var files_vernalable = report["files_vernalable"];
        var file_location = report["apk_location"];
        var app_category = appData.apk_category ? appData.apk_category : 'Not Available';
        //console.log("app category : " + app_category);
        var fv = [];
        for (var f in files_vernalable) {
            var s = files_vernalable[f].replace(file_location, "");
            fv.push(s);
        }

        var responceObj = {
            _id: appData._id,
            title: appData.title,
            apk_status: vulnerable,
            trust_manager: trust_manager,
            seeds: seeds,
            v_end_points: v_end_points,
            apk_package: apk_package,
            files_vernalable: fv,
            app_category: app_category
        };
        res.send(responceObj);
    });
};

exports.getSAReportFile = function (req, res) {
    Apk.findOne({_id: req.params._id}).exec(function (err, appData) {
        if (err) {
            res.status(400);
            return res.send({reason: err.toString()});
        }
        var full_report = appData.SA_report;
        res.set('Content-Type', 'application/json');
        var responceObj = {
            _id: appData._id,
            title: appData.title,
            SA_report: full_report
        };
        res.send(responceObj);
    });
};

exports.getSAReportTree = function (req, res) {
    Apk.findOne({_id: req.params._id}).exec(function (err, appData) {
        console.log(req.params._id);
        if (err) {
            res.status(400);
            return res.send({reason: err.toString()});
        }
        var report = JSON.parse(appData.SA_report);
        var seed_trees = report["seed_trees"];
        console.log(req.params._seedId);
        //console.log(seed_trees);
        var responceObj = {};
        for (var i in seed_trees) {
            var s = seed_trees[i];
            console.log(s["name"]);
            if (s["name"] === req.params._seedId) {
                responceObj = s;
                break;
            }
        }
        res.set('Content-Type', 'application/json');
        res.send(responceObj);
    });
};

exports.getSIGReport = function (req, res) {
    Apk.findOne({_id: req.params._id}).exec(function (err, appData) {
        if (err) {
            res.status(400);
            return res.send({reason: err.toString()});
        }
        var responceObj = {
            _id: appData._id,
            title: appData.title,
            SIG_report: appData.SIG_report
        }
        res.send(responceObj);
    });
};

/*

 shell.echo('hello world');
 shell.echo(process.cwd());
 shell.cd(process.cwd());
 //console.log(shell.ls());

 //shell.ls('./');

 */
function trigerFileProcessing(file_id) {
    //console.log(file_id);
    checkIfFileExists(file_id);
}

function checkIfFileExists(file_id) {
    var path = config.uploadAPKLocation + '/' + file_id + '.apk';
    fsExists(path, function (err, result) {
        if (err) throw err; // err will always be null
        if (result) {
            //console.log(path+" is present.");
            decompileAPK(file_id);
        } else {
            console.log(path + " is not present.");
            updateSAinDB(file_id, true, "ERROR : The Report cannot be generated as the APK file was not found in the server.");
            updateSIGinDB(file_id, true, "ERROR : The Report cannot be generated as the APK file was not found in the server.");
        }
    })
}

function decompileAPK(file_id) {
    var input_file = config.uploadAPKLocation + '/' + file_id + '.apk';
    var output_folder = config.apkDecompileLocation + '/' + file_id;
    var apk_tool = config.apkTool;
    var command = apk_tool + " d " + input_file + " -fo " + output_folder; // remove -fo in production and add d -f
    console.log(command);
    const child = exec(command, function (error, stdout, stderr) {
        //console.log("stdout: "+stdout);
        //console.log("stderr: "+stderr);
        if (error !== null) {
            console.log("exec error: error" + error);
        } else {
            console.log("Need to run SA and SIG next.");
            runSA(file_id, output_folder);
            runSIG(file_id, input_file, output_folder);
        }
    });

}

function runSA(file_id, apk_input_folder) {
    var SA_script_location = config.SA_script_location;
    var SA_output_location = config.SA_output_location;
    var output_file = SA_output_location + "/" + file_id + ".json";
    var options = {
        scriptPath: SA_script_location,
        args: [apk_input_folder, output_file, SA_script_location]
    };
    PythonShell.run('mfg_generator.py', options, function (err, results) {
        if (err) return err;
        // results is an array consisting of messages collected during execution
        //console.log("**************************************************************************************")
        //console.log('results: '+ results);
        //console.log("**************************************************************************************")
        //console.log("Load the result from "+output_file+" and push to DB.");
        fs.readFile(output_file, 'utf8', function (err, contents) {
            updateSAinDB(file_id, true, contents);
            var report = JSON.parse(contents);
            //console.log('SA DONE');
            //console.log(report);
            var package_name = report["apk_package"];
            //console.log(package_name);
            appCategory(file_id, package_name);
        });
    });
}

function runSIG(file_id, apk_input_folder) {
    var SIG_script_location = config.SIG_script_location;
    var SIG_output_location = config.SIG_output_location;
    //console.log(SIG_script_location);
    //console.log(SIG_output_location);
    console.log(apk_input_folder);
    var options = {
        scriptPath: SIG_script_location,
        args: [apk_input_folder, SIG_output_location]
    };
    PythonShell.run('get_field_type.py', options, function (err, results) {
        if (err) return err;
        var output_file = SIG_output_location + "/" + file_id + "_arff_output_complex.arff";
        console.log("File Name: " + output_file);
        fs.readFile(output_file, 'utf8', function (err, contents) {
            //console.log("File ***************************"+contents);
            if (contents === undefined)
                contents = "NO SIG output.";
            updateSIGinDB(file_id, true, contents);
            deleateAllFilesCreated(file_id);
        });
    });
}

function deleateAllFilesCreated(file_id) {
    //TODO: deleate all files created for both SA and SIG
}

function updateSAinDB(id, status, report) {
    //update SA in Database
    //console.log("update SA in Database"+id+" "+status+" "+report);
    //console.log(JSON.parse(report))
    Apk.update({_id: id}, {$set: {isSA_done: status, SA_report: report}}, function (err, data) {
        if (err) return err;
        console.log('update SA in Database: The response from Mongo was ', data);
    });
}

function updateSIGinDB(id, status, report) {
    //update SIG in Database
    //console.log("update SIG in Database"+id+" "+status+" "+report);
    Apk.update({_id: id}, {$set: {isSIG_done: status, SIG_report: report}}, function (err, data) {
        if (err) return err;
        console.log('update SIG in Database: The response from Mongo was ', data);
    });
}

function appCategory(id, apkPackage) {
    //console.log('inside appCategory'+apkPackage);
    var ds_category = 'none';
    //console.log("apk Package : " + apkPackage);
    var request = require('request');
    var cheerio = require('cheerio');
    request(config.play_category_finder + apkPackage, function (error, response, html) {
        if (!error && response.statusCode == 200) {
            //console.log("Connection OK");
            var $ = cheerio.load(html);
            $('a.category').each(function (i, element) {
                //console.log("in here");
                var rank = $(this).children('span').text();
                ds_category = rank;
                //console.log("category:" + ds_category);
                Apk.update({_id: id}, {$set: {apk_category: ds_category}}, function (err, data) {
                    if (err) return err;
                    console.log('update Category in Database: The response from Mongo was ', data);
                });
            });
        }
    });
    return ds_category;
}