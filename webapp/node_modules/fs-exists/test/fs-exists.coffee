fs = require "fs"
fsExists = require "../lib/fs-exists"
async = require "async"

paths = [
  process.env.HOME,
  __filename,
  __dirname,
  "/",
  "/probably.non-existing",
  "/THE BIG BLACK VOID",
  "/dev/null"
  "/etc"
  "/home"
  process.env.HOME + "/non-existing-path.probably"
  "/H9Wf486Jz1uiW57l6f1G",
  "gvcnciXE06n7hxKrpQrm",
  "./YIedRj5JERvMUL78qeeK",
  "../K6hY5htYMkxVFmvJDvL0",
  "../../BLnCrh1hLzi0TXZVI5T3",
  "../../../zGmEZqeaduBW7py7nBmr",
]

asyncEqual = (functions, next) ->
  doFunc = (func, next) -> func next
  async.map functions, doFunc, (err, values) ->
    return next err if err
    return next null, false for value in values when value isnt values[0]
    return next null, true

describe "fs-exists", ->
  it "should mirror the result of fs.exists", (next) ->
    checkEqualResults = (path, next) ->
      fsExistsTest = (next) -> 
        fsExists path, next
      nativeTest = (next) ->
        fs.exists path, (pathExists) -> 
          next null, pathExists
      asyncEqual [fsExistsTest,nativeTest], next
    async.map paths, checkEqualResults, (err, results) ->
      return next err if err
      for i in [0...paths.length]
        return next new Error "Results for path #{paths[i]} were not equal." unless results[i]
      next null