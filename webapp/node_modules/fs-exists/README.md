# fs-exists [![Build Status](https://travis-ci.org/meryn/fs-exists.png?branch=master)](https://travis-ci.org/meryn/fs-exists)

Wraps Node.js' native `fs.exists` so callback is called with `(err, result)` instead of just `(result)`.  
Since it's just wrapping `fs.exists`, the `err` argument will always be `null`.

I developed the module to have a function that can be easily adapted to return a promise (for example with `faithful.adapt` from my [Faithful](https://github.com/meryn/faithful) project), but you may find other uses for it.

## Usage

```javascript
fsExists = require('fs-exists')
fsExists(path, function(err, result) {
  if (err) throw err; // err will always be null
  if(result)
    console.log "the entry exists"
  else
    console.log "the entry does not exist"
})
```

## License

fs-exists is released under the [MIT License](http://opensource.org/licenses/MIT).  
Copyright (c) 2013 Meryn Stol  