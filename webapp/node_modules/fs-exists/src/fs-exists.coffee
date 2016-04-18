fs = require "fs"

module.exports = fsExists = (path, callback) ->
  fs.exists path, (result) ->
    callback null, result