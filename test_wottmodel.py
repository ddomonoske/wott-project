from wottmodel import *
from pathlib import Path
from test_helpers import *
from wottattributes import *


def test_Rider_valid_attributes() -> int:
    try:
        attributes = {
            RiderAttributes.RIDERID: 1,
            RiderAttributes.FIRSTNAME: "David",
            RiderAttributes.LASTNAME: "Domonoske",
            RiderAttributes.WEIGHT: 90,
            RiderAttributes.FTP: 380,
            RiderAttributes.CDA: 0.19,
            RiderAttributes.WPRIME: 20
        }
        rider = Rider(**attributes)
        printSuccess("test_Rider_valid_attributes")
        return 0
    except:
        printFailure("test_Rider_valid_attributes")
        return 1

def test_Rider_invalid_attributes() -> int:
    try:
        attributes = {
            RiderAttributes.RIDERID: 1,
            RiderAttributes.FIRSTNAME: "David",
            RiderAttributes.LASTNAME: "Domonoske",
            RiderAttributes.WEIGHT: 90,
            RiderAttributes.FTP: 380,
            RiderAttributes.CDA: 0.19,
            RiderAttributes.WPRIME: 20,
            "invalidAttribute": 0
        }
        rider = Rider(**attributes)
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
            RiderAttributes.RIDERID: 1,
            RiderAttributes.FIRSTNAME: "David",
            RiderAttributes.LASTNAME: "Domonoske",
            RiderAttributes.WEIGHT: 90,
            RiderAttributes.FTP: 380,
            RiderAttributes.CDA: 0.19,
            RiderAttributes.WPRIME: 20
        }
        rider = Rider(**attributes)
        strDict = rider.getStrAttributeDict()
        if all(key in strDict for key in attributes.keys()):
            printSuccess("test_Rider_getStrAttributeDict")
            return 0
        else:
            raise Exception
    except:
        printFailure("test_Rider_getStrAttributeDict")
        return 1

def test_Environment_valid_attributes() -> int:
    try:
        attributes = {
            EnvirAttributes.ENVIRID: 1,
            EnvirAttributes.ENVIRNAME: "Panam Games Santiago",
            EnvirAttributes.AIRDENSITY: "1.105",
            EnvirAttributes.CRR: 0.0015,
            EnvirAttributes.MECHLOSSES: 0.02
        }
        envir = Environment(**attributes)
        printSuccess("test_Environment_valid_attributes")
        return 0
    except:
        printFailure("test_Environment_valid_attributes")
        return 1

def test_Environment_invalid_attributes() -> int:
    try:
        attributes = {
            EnvirAttributes.ENVIRID: 1,
            EnvirAttributes.ENVIRNAME: "Panam Games Santiago",
            EnvirAttributes.AIRDENSITY: "1.105",
            EnvirAttributes.CRR: 0.0015,
            EnvirAttributes.MECHLOSSES: 0.02,
            "invalidAttribute": 0
        }
        envir = Environment(**attributes)
        printFailure("test_Environment_invalid_attributes")
        return 1
    except AttributeError:
        printSuccess("test_Environment_invalid_attributes")
        return 0
    except:
        printFailure("test_Environment_invalid_attributes")
        return 1

def test_Environment_getStrAttributeDict() -> int:
    try:
        attributes = {
            EnvirAttributes.ENVIRID: 1,
            EnvirAttributes.ENVIRNAME: "Panam Games Santiago",
            EnvirAttributes.AIRDENSITY: "1.105",
            EnvirAttributes.CRR: 0.0015,
            EnvirAttributes.MECHLOSSES: 0.02
        }
        envir = Environment(**attributes)
        strDict = envir.getStrAttributeDict()
        if all(key in strDict for key in attributes.keys()):
            printSuccess("test_Environment_getStrAttributeDict")
            return 0
        else:
            raise Exception
    except:
        printFailure("test_Environment_getStrAttributeDict")
        return 1

def test_Simulation_valid_attributes() -> int:
    try:
        attributes = {
            SimAttributes.SIMID: 1,
            SimAttributes.SIMNAME: "Dave Panams IP",
            SimAttributes.RIDER: Rider(0, firstName="David"),
            SimAttributes.ENVIR: Environment(0, envirName="Santiago")
        }
        sim = Simulation(**attributes)
        printSuccess("test_Simulation_valid_attributes")
        return 0
    except:
        printFailure("test_Simulation_valid_attributes")
        return 1

def test_Simulation_invalid_attributes() -> int:
    try:
        attributes = {
            SimAttributes.SIMID: 1,
            SimAttributes.SIMNAME: "Dave Panams IP",
            SimAttributes.RIDER: Rider(0, firstName="David"),
            SimAttributes.ENVIR: Environment(0, envirName="Santiago"),
            "invalidAttribute": 0
        }
        sim = Simulation(**attributes)
        printFailure("test_Simulation_invalid_attributes")
        return 1
    except AttributeError:
        printSuccess("test_Simulation_invalid_attributes")
        return 0
    except:
        printFailure("test_Simulation_invalid_attributes")
        return 1

def test_Simulation_getStrAttributeDict() -> int:
    try:
        attributes = {
            SimAttributes.SIMID: 1,
            SimAttributes.SIMNAME: "Dave Panams IP",
            SimAttributes.RIDER: Rider(0, firstName="David"),
            SimAttributes.ENVIR: Environment(8, envirName="San Juan")
        }
        sim = Simulation(**attributes)
        strDict = sim.getStrAttributeDict()
        if all(key in strDict for key in attributes.keys()):
            printSuccess("test_Simulation_getStrAttributeDict")
            return 0
        else:
            raise Exception
    except:
        printFailure("test_Simulation_getStrAttributeDict")
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
             test_Environment_valid_attributes,
             test_Environment_invalid_attributes,
             test_Environment_getStrAttributeDict,
             test_Simulation_valid_attributes,
             test_Simulation_invalid_attributes,
             test_Simulation_getStrAttributeDict,
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
def main():
    failedTests = 0
    for test in test_list:
        if test():
            failedTests += 1

    if failedTests:
        printFailure(f"{bcolors.EMPH}\n{failedTests} test(s) failed")
        printSuccess(f"{bcolors.EMPH}{len(test_list)-failedTests} test(s) passed")
    else:
        printSuccess(f"{bcolors.EMPH}\nAll {len(test_list)} tests passed")

if __name__ == '__main__':
    main()
