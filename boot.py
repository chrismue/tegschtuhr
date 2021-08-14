# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import uos, machine
# uos.dupterm(None, 1) # disable REPL on UART(0)
# import webrepl
# webrepl.start()
import gc
gc.collect()

import os
if "next" in os.listdir("."):
    if '.version' in os.listdir("next"):
        from ota_updater import OTAUpdater
        otaUpdater = OTAUpdater('https://github.com/chrismue/tegschtuhr', main_dir="/")
        otaUpdater.install_new_version_if_downloaded()
print("No Folder 'next' found for update")
