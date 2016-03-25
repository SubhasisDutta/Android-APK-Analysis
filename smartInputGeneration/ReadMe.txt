Generate smart inputs. Output in "smartInput.db" file.

$ cd ./smartGeneration 
$ python get_field_type.py /location/of/apk/folder/example.apk
$ cat smartInput.db


Note: Before executing python file (get_field_type.py), please make sure decompiled folder for apk file must be there in the same location. 
			To obtain decompile code:
			$ ./apktool d /location/of/apk/folder/example.apk /location/of/decoded/folder/example
