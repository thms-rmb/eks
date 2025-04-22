# Installing MarcEdit on MacOS

Though MarcEdit provides installation instructions for MacOS, I could not get these to work properly.

What does work is to just utilize Wine and the Windows installer directly instead.

## Dependencies

+ Homebrew

+ Wine

    ```shell
    brew install wine-stable
    ```

## Instructions

1. Set up a new Wine prefix

    ```shell
    mkdir --parents ~/.winebottles/marcedit
    ```

2. Download the MarcEdit User Only Installation (Self Contained) for Windows variant: https://marcedit.reeset.net/downloads

3. Install MarcEdit into the newly made Wine prefix, following the instructions and picking defaults when asked.

    ```shell
    WINEPREFIX=~/.winebottles/marcedit wine ~/Downloads/MarcEdit_7_7_User_Install.exe
    ```

4. To obtain the launch information, you can inspect the `.desktop` file created by the installer:

    ```shell
    cat ~/Desktop/MarcEdit.desktop
    ```

    ```
    [Desktop Entry]
    Name=MarcEdit
    Exec=env WINEPREFIX="/Users/thmsrmb/.winebottles/marcedit" wine C:\\\\users\\\\thmsrmb\\\\AppData\\\\Roaming\\\\MarcEdit\\ 7.7\\ \\(User\\)\\\\MarcEdit.exe 
    Type=Application
    StartupNotify=true
    Path=/Users/thmsrmb/.winebottles/marcedit/dosdevices/c:/users/thmsrmb/AppData/Roaming/MarcEdit 7.7 (User)/
    StartupWMClass=marcedit.exe
    ```

    Note the line beginning with `Exec=`, and grab the value.

5. Create an Application launcher for MarcEdit.

    Get the exec value from the `.desktop` file you inspected above.

    Next, open *Script Editor* and paste in the following:

    ```applescript
    tell application "Terminal"
        activate
        do script "{{VALUE}}"
    end tell
    ```

    Replace `{{VALUE}}` with the value you got from the `.desktop` file. Since it can contain `"`, you should replace those with single quotes `'` or just remove them.

    Verify that the script works when clicking the run button.

    Finally, do File -> Export... and choose *Application*  as the *File Format*, and save it in the *Applications* directory.
