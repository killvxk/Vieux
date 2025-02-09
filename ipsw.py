import os
import shutil
import bsdiff4
import plistlib
import device as localdevice
from pathlib import Path
from zipfile import ZipFile
from restore import restore64, restore32, pwndfumode

def readmanifest(path, flag):
    fn = path
    with open(fn, 'rb') as f:
        pl = plistlib.load(f)
    if flag:
        result = pl['ProductVersion']
    else:
        supportedModels = str(pl['SupportedProductTypes'])
        supportedModels1 = supportedModels.replace("[", "")
        supportedModels2 = supportedModels1.replace("'", "")
        result = supportedModels2.replace("]", "")
    return result


def removeFiles():
    randomfiles = ['errorlogshsh.txt', 'errorlogrestore.txt', 'ibss', 'ibec', 'resources/restoreFiles/baseband.bbfw', 'resources/restoreFiles/sep.im4p', 'resources/restoreFiles/apnonce.shsh', '']

    for item in randomfiles:
        if os.path.isfile(item):
            os.remove(item)
    if os.path.exists("IPSW"):
        shutil.rmtree("IPSW")
    if os.path.exists("Firmware"):
        shutil.rmtree("Firmware")
    if os.path.exists("custom"):
        shutil.rmtree('custom')

    dir_name = os.getcwd()
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith(".im4p"):
            os.remove(os.path.join(dir_name, item))
        elif item.endswith(".plist"):
            os.remove(os.path.join(dir_name, item))
        elif item.endswith(".dmg"):
            os.remove(os.path.join(dir_name, item))
        elif item.endswith(".shsh"):
            os.remove(os.path.join(dir_name, item))
        elif item.endswith(".shsh2"):
            os.remove(os.path.join(dir_name, item))
        elif item.endswith(".dfu"):
            os.remove(os.path.join(dir_name, item))

    print("Files cleaned.")

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

def unzipIPSW(fname):
    armv7 = ['iPhone4,1']
    armv7s = ['iPhone5,1', 'iPhone5,2']
    if os.path.exists("custom.ipsw"):
        os.remove("custom.ipsw")

    print("Starting IPSW unzipping")
    outputFolder = "IPSW"
    newpath = fname.rstrip()
    fname = str(newpath)
    testFile = os.path.exists(fname)
    if os.path.exists('IPSW'):
        shutil.rmtree('IPSW')
        os.mkdir('IPSW')
    elif not os.path.exists('IPSW'):
        os.mkdir('IPSW')

    while not testFile or not fname.endswith!=(".ipsw"):
        print("Invalid filepath/filename.\nPlease try again with a valid filepath/filename.")
        fname = input("Enter the path to the IPSW file (Or drag and drop the IPSW into this window):\n")
        newpath = fname.rstrip()
        fname = str(newpath)
        testFile = os.path.exists(fname)
    else:
        print("Continuing...")
    if testFile and fname.endswith(".ipsw"):
        if os.path.exists("resources/restoreFiles/igetnonce"):
            shutil.move("resources/restoreFiles/igetnonce", "igetnonce")
        if os.path.exists("resources/restoreFiles/tsschecker"):
            shutil.move("resources/restoreFiles/tsschecker", "tsschecker")
        if os.path.exists("resources/restoreFiles/futurerestore"):
            shutil.move("resources/restoreFiles/futurerestore", "futurerestore")
        if os.path.exists("resources/restoreFiles/irecovery"):
            shutil.move("resources/restoreFiles/irecovery", "irecovery")
        print("IPSW found at given path...")
        print("Cleaning up old files...")
        removeFiles()
        print("Unzipping..")
        with ZipFile(fname, 'r') as zip_ref:
            zip_ref.extractall(outputFolder)
        source = ("IPSW/Firmware/dfu/")
        dest1 = os.getcwd()

        files = os.listdir(source)

        for f in files:
            shutil.move(source + f, dest1)
        devicemodel = str(localdevice.getmodel())
        version = False
        supportedModels = str(readmanifest("IPSW/BuildManifest.plist", version))
        if supportedModels in armv7:
            createCustomIPSW32(fname)
        else:
            if supportedModels in armv7s:
                createCustomIPSW32(fname)
            else:
                arm64check = ('iPhone6,1', 'iPhone6,2', 'iPad4,1', 'iPad4,2', 'iPad4,3', 'iPad4,4', 'iPad4,5')
                if any(ext in supportedModels for ext in arm64check):
                    if any(ext in devicemodel for ext in arm64check):
                        pwndfumode()
                        createCustomIPSW64(fname, devicemodel)
                    else:
                        print("ERROR: Unsupported model...\nExiting...")
                        exit(82)
                else:
                    print("ERROR: Unsupported model...\nExiting...")
                    exit(82)
    else:
        print('\033[91m' + "ERROR: Not valid filepath...")
        print("ERROR: Try again" + '\033[0m')

def createCustomIPSW32(fname):
    if os.path.exists("resources/restoreFiles/futurerestore"):
        shutil.move("resources/restoreFiles/futurerestore", "futurerestore")
    print("Starting iBSS/iBEC patching")
    kloader10location = "resources/restoreFiles/kloader10"
    kloaderlocation = "resources/restoreFiles/kloader"
    patch_folder = Path("resources/patches/")
    phone52ibss = patch_folder / "ibss.iphone52.patch"
    phone51ibss = patch_folder / "ibss.iphone51.patch"
    phone4sibss6 = patch_folder / "ibss.iphone4,1.6.1.3.patch"
    phone4sibss8 = patch_folder / "ibss.iphone4,1.8.4.1.patch"
    version = True
    versionManifest = readmanifest("IPSW/BuildManifest.plist", version)
    version = False
    deviceManifest = readmanifest("IPSW/BuildManifest.plist", version)
    if "iPhone5,2" in deviceManifest or "iPhone5,1" in deviceManifest and "8.4.1" in versionManifest:
        print("Looks like you are downgrading an iPhone 5 to 8.4.1!")
        if "iPhone5,2" in deviceManifest:
            bsdiff4.file_patch_inplace("iBSS.n42.RELEASE.dfu", phone52ibss)
            shutil.copy("iBSS.n42.RELEASE.dfu", "ibss")
            model = "iPhone5,2"
        elif "iPhone5,1" in deviceManifest:
            bsdiff4.file_patch_inplace("iBSS.n41.RELEASE.dfu", phone51ibss)
            shutil.copy("iBSS.n41.RELEASE.dfu", "ibss")
            model = "iPhone5,1"
        ibsslocation = "ibss"
        device = "iPhone5"
    elif "6.1.3" in versionManifest or "8.4.1" in versionManifest and "iPhone4,1" in deviceManifest:
        device = "iPhone4s"
        model = "iPhone4,1"

    else:
        print('\033[91m' + "Im tired" + '\033[0m')
        exit(24)

    if device == "iPhone5":
        iosversion = "8.4.1"
        shutil.copy(fname, "custom.ipsw")
        localdevice.enterkdfumode(kloaderlocation, kloader10location, ibsslocation)
        restore32(model, iosversion)
    elif device == "iPhone4s":
        if "8.4.1" in versionManifest:
            print("Looks like you are downgrading an iPhone 4s to 8.4.1!")
            iosversion = "8.4.1"
            bsdiff4.file_patch_inplace("iBSS.n94.RELEASE.dfu", phone4sibss8)
            shutil.copy("iBSS.n94.RELEASE.dfu", "ibss")
            ibsslocation = "ibss"
            shutil.copy(fname, "custom.ipsw")
            localdevice.enterkdfumode(kloaderlocation, kloader10location, ibsslocation)
            restore32(model, iosversion)
        elif "6.1.3" in versionManifest:
            print("Looks like you are downgrading an iPhone 4s to 6.1.3!")
            iosversion = "6.1.3"
            bsdiff4.file_patch_inplace("iBSS.n94ap.RELEASE.dfu", phone4sibss6)
            shutil.copy("iBSS.n94ap.RELEASE.dfu", "ibss")
            ibsslocation = "ibss"
            shutil.copy(fname, "custom.ipsw")
            localdevice.enterkdfumode(kloaderlocation, kloader10location, ibsslocation)
            restore32(model, iosversion)
        else:
            print("=(")
            exit(2)
    else:
        print("=(")
        exit(2)
def createCustomIPSW64(fname, devicemodel):
    print("Starting iBSS/iBEC patching")
    patch_folder = Path("resources/patches/")
    phoneibec = patch_folder / "ibec5s.patch"
    phoneibss = patch_folder / "ibss5s.patch"
    ipadminiibec = patch_folder / "ibec_ipad4b.patch"
    ipadminiibss = patch_folder / "ibss_ipad4b.patch"
    ipadairibec = patch_folder / "ibec_ipad4.patch"
    ipadairibss = patch_folder / "ibss_ipad4.patch"
    version = True
    versionManifest = readmanifest("IPSW/BuildManifest.plist", version)
    version = False
    deviceManifest = readmanifest("IPSW/BuildManifest.plist", version)
    if "iPhone" in deviceManifest and "10.3.3" in versionManifest:
        print("Looks like you are downgrading an iPhone 5s to 10.3.3!")
        bsdiff4.file_patch_inplace("iBEC.iphone6.RELEASE.im4p", phoneibec)
        bsdiff4.file_patch_inplace("iBSS.iphone6.RELEASE.im4p", phoneibss)
        device = "iPhone5s"
    elif "iPad" in deviceManifest and "10.3.3" in versionManifest:
        if devicemodel == "iPad4,1" or devicemodel == "iPad4,2" or devicemodel == "iPad4,3":
            print("Looks like you are downgrading an iPad Air to 10.3.3!")
            bsdiff4.file_patch_inplace("iBEC.ipad4.RELEASE.im4p", ipadairibec)
            bsdiff4.file_patch_inplace("iBSS.ipad4.RELEASE.im4p", ipadairibss)
            device = "iPadAir"
        elif devicemodel == "iPad4,4" or devicemodel == "iPad4,5":
            print("Looks like you are downgrading an iPad Mini 2 to 10.3.3!")
            bsdiff4.file_patch_inplace("iBEC.ipad4b.RELEASE.im4p", ipadminiibec)
            bsdiff4.file_patch_inplace("iBSS.ipad4b.RELEASE.im4p", ipadminiibss)
            device = "iPadMini"
        else:
            print("ERROR: Unknown input. Exiting purely because you can't read and that's sad...")
            print("ERROR: Exiting...")
            exit(1)
    else:
        print("Varible 'device' was not set. Please make sure IPSW file name is default/device is connected and try again")
        exit(55555)
    print("Patched iBSS/iBEC")
    print("About to re-build IPSW")

    if device == "iPhone5s":
        shutil.move("iBEC.iphone6.RELEASE.im4p", "IPSW/Firmware/dfu/")
        shutil.move("iBSS.iphone6.RELEASE.im4p", "IPSW/Firmware/dfu/")
        shutil.move("IPSW/Firmware/Mav7Mav8-7.60.00.Release.bbfw", "resources/restoreFiles/baseband.bbfw")
        if devicemodel == "iPhone6,1":
            shutil.move("IPSW/Firmware/all_flash/sep-firmware.n51.RELEASE.im4p", "resources/restoreFiles/sep.im4p")
        elif devicemodel == "iPhone6,2":
            shutil.move("IPSW/Firmware/all_flash/sep-firmware.n53.RELEASE.im4p", "resources/restoreFiles/sep.im4p")
        touch("IPSW/Firmware/usr/local/standalone/blankfile")
        with ZipFile('custom.ipsw', 'w') as zipObj2:
            os.chdir("IPSW")
            zipObj2.write('Restore.plist')
            zipObj2.write('kernelcache.release.iphone8b')
            zipObj2.write('kernelcache.release.iphone6')
            zipObj2.write('BuildManifest.plist')
            zipObj2.write('058-75381-062.dmg')
            zipObj2.write('058-74940-063.dmg')
            zipObj2.write('058-74917-062.dmg')
            zipObj2.write('._058-74917-062.dmg')
            for folderName, subfolders, filenames in os.walk("Firmware"):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    zipObj2.write(filePath)
            if os.path.exists("IPSW/custom.ipsw"):
                shutil.move("IPSW/custom.ipsw", "custom.ipsw")
            os.chdir("..")
        restore64(devicemodel)

    elif device == "iPadAir" or device == "iPadMini":
        if devicemodel == "iPad4,1" or devicemodel == "iPad4,2" or devicemodel == "iPad4,3":
            shutil.move("iBEC.ipad4.RELEASE.im4p", "IPSW/Firmware/dfu/")
            shutil.move("iBSS.ipad4.RELEASE.im4p", "IPSW/Firmware/dfu/")
            if devicemodel == "iPad4,1":
                shutil.move("IPSW/Firmware/all_flash/sep-firmware.j71.RELEASE.im4p", "resources/restoreFiles/sep.im4p")
            elif devicemodel == "iPad4,2":
                shutil.move("IPSW/Firmware/all_flash/sep-firmware.j72.RELEASE.im4p", "resources/restoreFiles/sep.im4p")
                shutil.move("IPSW/Firmware/Mav7Mav8-7.60.00.Release.bbfw", "resources/restoreFiles/baseband.bbfw")
            elif devicemodel == "iPad4,3":
                shutil.move("IPSW/Firmware/all_flash/sep-firmware.j73.RELEASE.im4p", "resources/restoreFiles/sep.im4p")
                shutil.move("IPSW/Firmware/Mav7Mav8-7.60.00.Release.bbfw", "resources/restoreFiles/baseband.bbfw")
        elif devicemodel == "iPad4,4" or devicemodel == "iPad4,5":
            shutil.move("iBEC.ipad4b.RELEASE.im4p", "IPSW/Firmware/dfu/")
            shutil.move("iBSS.ipad4b.RELEASE.im4p", "IPSW/Firmware/dfu/")
            if devicemodel == "iPad4,4":
                shutil.move("IPSW/Firmware/all_flash/sep-firmware.j85.RELEASE.im4p", "resources/restoreFiles/sep.im4p")
            elif devicemodel == "iPad4,5":
                shutil.move("IPSW/Firmware/all_flash/sep-firmware.j86.RELEASE.im4p", "resources/restoreFiles/sep.im4p")
                shutil.move("IPSW/Firmware/Mav7Mav8-7.60.00.Release.bbfw", "resources/restoreFiles/baseband.bbfw")
        touch("IPSW/Firmware/usr/local/standalone/blankfile")

        with ZipFile('custom.ipsw', 'w') as zipObj2:
            os.chdir("IPSW")
            zipObj2.write('Restore.plist')
            zipObj2.write('kernelcache.release.ipad4')
            zipObj2.write('kernelcache.release.ipad4b')
            zipObj2.write('BuildManifest.plist')
            zipObj2.write('058-75381-062.dmg')
            zipObj2.write('058-75094-062.dmg')
            zipObj2.write('058-74940-063.dmg')
            zipObj2.write('._058-75094-062.dmg')
            for folderName, subfolders, filenames in os.walk("Firmware"):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    zipObj2.write(filePath)
            os.chdir("..")
            if os.path.exists("IPSW/custom.ipsw"):
                shutil.move("IPSW/custom.ipsw", "custom.ipsw")
        restore64(devicemodel)
    else:
        print('\033[91m' + "something broke lmao" + '\033[0m')
        exit(1)
