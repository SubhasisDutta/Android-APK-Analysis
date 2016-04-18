# SMV-Hunter
==========
Set of tools for performing large-scale automated detection of SSL/TLS man-in-the-middle vulnerabilities in Android apps.

[NDSS 2014 Paper](http://www.internetsociety.org/doc/smv-hunter-large-scale-automated-detection-ssltls-man-middle-vulnerabilities-android-apps)

# Environment
==========
1. Ubuntu v12.04+
2. Apktool v1
3. Python v2.7
4. Java SDK v1.4+
5. Android tools (adb, emulator, android)

# Execution
==========

1. Decompile apk file using Apktool with folder name equal to the apk file name.

    ```
    $ cd ~/SMVHunter/apktool  
    $ ./apktool d /location/of/apk/folder/example.apk /location/of/decoded/folder/example.apk
    ```

2. Run static analysis to generate list of entry points to vulnerable apk. Output in "output.db" file.

    ```
    $ cd ~/SMVHunter/static  
    $ python mfg_generator.py /location/of/decoded/folder/example.apk
    $ cat output.db
    ```

3. Generate smart inputs. Output in "smartInput.db" file.

    ```
    $ cd ~/SMVHunter/smart_input_generation  
    $ python get_field_type.py /location/of/apk/folder/example.apk
    $ cat smartInput.db
    ```

4. Start emulator(s)

    ```
    $ cd ~/SMVHunter/dynamic  
    $ ./startgoogle.sh <emulator_name>
    ```

5. Setup MITM proxy as per Section V.C of paper.

6. Run dynamic analysis.
   1. Set items "adb.props" file.
   
    ```
    $ cd ~/SMVHunter/dynamic  
    $ vi adb.props
    ```

   2. Execute dynamic analysis

    ```
    $ cd ~/SMVHunter/dynamic  
    $ java -jar smvhunter_dymanic.jar
    ```

7. Perform correlative analysis using data in "correlative_analysis" folder as per "adb.props".


