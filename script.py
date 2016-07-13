import requests, getpass, re
import os.path
import os
import time, json
import platform
from os.path import expanduser

def setSkin(session, skin, uuid, accessToken):
    url = "https://api.mojang.com/user/profile/" + uuid + "/skin"
    data = {"file" : skin.read()}

    r = session.put(url, files = data, data = {"model" : "steve"}, headers = {"Authorization" : "Bearer " + accessToken})
    print(r.text)
    if r.status_code == 200 or r.status_code == 302 or r.status_code == 204:
        print("Success !")
        return True
    else:
        print("Uh oh... Didn't work well... (server answered " + str(r.status_code) + ")")
        print("Output :")
        print(r.text)
        return False


def downloadSkinData(uuid, signatures):
    urlComplement = ""
    if signatures:
        urlComplement = "?unsigned=false"

    r = requests.get("https://sessionserver.mojang.com/session/minecraft/profile/" + uuid + urlComplement)
    return r.text
 
def loadSkin(path, accessToken, uuid, signatures = False):
    try:
        with open(path, "rb") as f:
            try:
                if setSkin(session, f, uuid, accessToken):
                    return downloadSkinData(uuid, signatures)
            except Exception as e:
                print("Error : ", e)
    except Exception as e:
        print("Error : ", e)
 
    return None

def findMinecraftPath():
    system = platform.system()
    if system == "Linux":
        return expanduser("~") + "/.minecraft"
    elif system == "Windows":
        return os.getenv('APPDATA') + "/.minecraft"
    elif system == "Darwin":
        return expanduser("~") + "/Library/Application Support/minecraft"
    else:
        return expanduser("~") + "/.minecraft"

 
session = requests.Session()
print("Reading .minecraft file...")
home = findMinecraftPath()
print("Trying to access .minecraft directory here : " + home)

accessToken = uuid = None

if os.path.exists(home + "/launcher_profiles.json"):
    with open(home + "/launcher_profiles.json", "r") as f:
        data = json.load(f)
        authDb = data["authenticationDatabase"]
        user = list(authDb.values())[0]
        if user is not None:
            print("Username :", user["displayName"])
            print("UUID :", user["uuid"])
            print("Secret token :", user["accessToken"])

            accessToken = user["accessToken"]
            uuid = user["uuid"]

if accessToken == None:
    accessToken = input("No access token found. Access Token ? ")
if uuid == None:
    uuid = input("No UUID found. UUID ? ")

uuid = uuid.replace("-", "")

signatures = False
sig = input("Do you want to get signatures for the skins ? [y/N] ")
if sig == "Y" or sig == "y":
    signatures = True

print("Select mode :")
print("[1] : Skin by skin")
print("[2] : Load list")
 
choice = None
while choice != "1" and choice != "2":
    choice = input("Your choice ? ")
 
if choice == "1":
    path = None
    while path != "end":
        path = input("Path of the skin ? [end to stop] ")
        if path == "end":
            break
 
        data = loadSkin(path, accessToken, uuid, signatures)
        print("Mojang data : " + data)
else:
    first = True
    path = input("Path of the skin directory : ")
    if not os.path.isdir(path):
        print("File is not a directory !")
    else:
        targetFile = path + "/output.txt"
        if os.path.isfile(targetFile) or os.path.isdir(targetFile):
            input(targetFile + " already exists, please move it or remove it then press enter.")
 
        with open(targetFile, "w") as f:
            for skin in os.listdir(path):
                if os.path.isfile(path + "/" + skin):
                    if skin.endswith(".png"):
                        if not first:
                            print("Waiting 60 seconds (api rate limit)")
                            time.sleep(60)
 
                        first = False
                        print("Found skin " + skin + " !")
                        data = loadSkin(path + "/" + skin, accessToken, uuid, signatures)
 
                        if data != None:
                            f.write(skin + " => " + data + "\n")
                            print(skin + " => " + data)
