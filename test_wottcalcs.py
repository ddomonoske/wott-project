from wottcalcs import *
from test_helpers import *
import inspect


def test_IPCalculator_calcPowerForce() -> int:
    try:
        attributes = {
            "CdA": 0.195,
            "airDensity": 1.12,
            "massKG": 100,
            "Crr": 0.002,
            "mechLoss": 0.02,
            "powerPlan": [(0,500),
                          (1,1000),
                          (3,1200),
                          (7,1000),
                          (15,800),
                          (20,700),
                          (45,360)]
        }
        ipc = IPCalculator(**attributes)

        for velocity in [0,3,10,20]:
            for time in [0,0.5,1,5,30,60]:
                if ipc.calcPowerForce(velocity, time) > ipc.maxForce:
                    raise Exception

        printSuccess(inspect.currentframe().f_code.co_name)
        return 0
    except:
        printFailure(inspect.currentframe().f_code.co_name)
        return 1

test_list = [test_IPCalculator_calcPowerForce]

# run all tests
def main():
    print("Running wottcalcs tests")
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
