from wottmodel import *
from pathlib import Path

# colors from blender
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    EMPH = BOLD+UNDERLINE

def printSuccess(text: str = "success"):
    print(f"{bcolors.OKGREEN}{text}{bcolors.ENDC}")

def printFailure(text: str = "failure"):
    print(f"{bcolors.FAIL}{text}{bcolors.ENDC}")

def test_Rider_valid_attributes() -> int:
    try:
        attributes = {
            Rider.attributes.RIDERID: 1,
            Rider.attributes.FIRSTNAME: "David",
            Rider.attributes.LASTNAME: "Domonoske",
            Rider.attributes.WEIGHT: 90,
            Rider.attributes.FTP: 380,
            Rider.attributes.CDA: 0.19,
            Rider.attributes.WPRIME: 20
        }
        rider = Rider(0, attributeDict=attributes)
        printSuccess("test_Rider_valid_attributes")
        return 0
    except:
        printFailure("test_Rider_valid_attributes")
        return 1

def test_Rider_invalid_attributes() -> int:
    try:
        attributes = {
            Rider.attributes.RIDERID: 1,
            Rider.attributes.FIRSTNAME: "David",
            Rider.attributes.LASTNAME: "Domonoske",
            Rider.attributes.WEIGHT: 90,
            Rider.attributes.FTP: 380,
            Rider.attributes.CDA: 0.19,
            Rider.attributes.WPRIME: 20,
            "invalidAttribute": 0
        }
        rider = Rider(1, attributeDict=attributes)
        printFailure("test_Rider_invalid_attributes")
        return 1
    except AttributeError:
        printSuccess("test_Rider_invalid_attributes")
        return 0
    except:
        printFailure("test_Rider_invalid_attributes")
        return 1

def test_Rider_getStrAttributeDict() -> int:
    try:
        attributes = {
            Rider.attributes.RIDERID: 1,
            Rider.attributes.FIRSTNAME: "David",
            Rider.attributes.LASTNAME: "Domonoske",
            Rider.attributes.WEIGHT: 90,
            Rider.attributes.FTP: 380,
            Rider.attributes.CDA: 0.19,
            Rider.attributes.WPRIME: 20
        }
        rider = Rider(0, attributeDict=attributes)
        strDict = rider.getStrAttributeDict()
        if all(key in strDict for key in Rider.keyList):
            printSuccess("test_Rider_getStrAttributeDict")
            return 0
        else:
            raise Exception
    except:
        printFailure("test_Rider_getStrAttributeDict")
        return 1

def test_saveObject_loadObject() -> int:
    # instanciate model with a test directory
    testDirectory = Path.cwd() / "wott_test_saveObject_loadObject"
    model = Model(str(testDirectory))

    ridersFile = testDirectory / "ridersFile"
    testObject = ["this","is","my","data"]
    model.saveObject(filePath=ridersFile, obj=testObject)

    returnObject = model.loadObject(ridersFile)

    # delete file and directory
    ridersFile.unlink()
    testDirectory.rmdir()

    if (returnObject == testObject):
        printSuccess("test_saveObject_loadObject")
        return 0
    else:
        printFailure("test_saveObject_loadObject")
        return 1

# TODO make these do more then the absolute barebones calls
def test_loadRiders() -> int:
    try:
        model = Model()
        model.loadRiders()
        printSuccess("test_loadRiders")
        return 0
    except:
        printFailure("test_loadRiders")
        return 1

def test_loadEnvirs() -> int:
    try:
        model = Model()
        model.loadEnvirs()
        printSuccess("test_loadEnvirs")
        return 0
    except:
        printFailure("test_loadEnvirs")
        return 1

def test_loadSims() -> int:
    try:
        model = Model()
        model.loadSims()
        printSuccess("test_loadSims")
        return 0
    except:
        printFailure("test_loadSims")
        return 1

def test_loadModel() -> int:
    try:
        model = Model()
        model.loadModel()
        printSuccess("test_loadModel")
        return 0
    except:
        printFailure("test_loadModel")
        return 1

def test_saveRiders() -> int:
    try:
        model = Model()
        model.saveRiders()
        printSuccess("test_saveRiders")
        return 0
    except:
        printFailure("test_saveRiders")
        return 1

def test_saveEnvirs() -> int:
    try:
        model = Model()
        model.saveEnvirs()
        printSuccess("test_saveEnvirs")
        return 0
    except:
        printFailure("test_saveEnvirs")
        return 1

def test_saveSims() -> int:
    try:
        model = Model()
        model.saveSims()
        printSuccess("test_saveSims")
        return 0
    except:
        printFailure("test_saveSims")
        return 1

def test_saveModel() -> int:
    try:
        model = Model()
        model.saveModel()
        printSuccess("test_saveModel")
        return 0
    except:
        printFailure("test_saveModel")
        return 1


test_list = [test_Rider_valid_attributes,
             test_Rider_invalid_attributes,
             test_Rider_getStrAttributeDict,
             test_saveObject_loadObject,
             test_loadRiders,
             test_loadEnvirs,
             test_loadSims,
             test_loadModel,
             test_saveRiders,
             test_saveEnvirs,
             test_saveSims,
             test_saveModel]

# run all tests
if __name__ == '__main__':
    failedTests = 0
    for test in test_list:
        if test():
            failedTests += 1

    if failedTests:
        printFailure(f"{bcolors.EMPH}\n{failedTests} test(s) failed")
        printSuccess(f"{bcolors.EMPH}{len(test_list)-failedTests} test(s) passed")
    else:
        printSuccess(f"{bcolors.EMPH}\nAll {len(test_list)} tests passed")
