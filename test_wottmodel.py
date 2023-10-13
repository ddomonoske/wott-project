from wottmodel import *

# TODO make these do more then the absolute barebones call

def test_loadModel():
    print("Test loadModel")
    model = Model()
    model.loadModel()

def test_loadRiders():
    print("Test loadRiders")
    model = Model()
    model.loadRiders()

def test_loadEnvirs():
    print("Test loadEnvirs")
    model = Model()
    model.loadEnvirs()

def test_loadSims():
    print("Test loadSims")
    model = Model()
    model.loadSims()

def test_saveModel():
    print("Test saveModel")
    model = Model()
    model.saveModel()

def test_saveRiders():
    print("Test saveRiders")
    model = Model()
    model.saveRiders()

def test_saveEnvirs():
    print("Test saveEnvirs")
    model = Model()
    model.saveEnvirs()

def test_saveSims():
    print("Test saveSims")
    model = Model()
    model.saveSims()

test_list = [test_loadRiders,
             test_loadEnvirs,
             test_loadSims,
             test_loadModel,
             test_saveRiders,
             test_saveEnvirs,
             test_saveSims,
             test_saveModel]

# run all tests
if __name__ == '__main__':
    for test in test_list:
        test()
