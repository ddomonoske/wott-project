from wottcalcs import *
from test_helpers import *
from wottattributes import *
import inspect
import matplotlib.pyplot as plt


def test_IPCalculator_calcPedalForce() -> int:
    try:
        attributes = {
            IPCalcAttributes.CDA: 0.195,
            IPCalcAttributes.AIRDENSITY: 1.12,
            IPCalcAttributes.MASSKG: 100,
            IPCalcAttributes.CRR: 0.002,
            IPCalcAttributes.MECHLOSSES: 0.02,
            IPCalcAttributes.POWERPLAN: [(0,500,1),
                                         (1,988,14),
                                         (15,550,20),
                                         (35,458,100),
                                         (135,523,120)]
        }
        ipc = IPCalculator(**attributes)

        for velocity in [0,3,10,20]:
            for time in [0,0.5,1,5,30,60]:
                if ipc.calcPedalForce(velocity, time) > ipc.maxForce:
                    raise Exception

        printSuccess(inspect.currentframe().f_code.co_name)
        return 0
    except:
        printFailure(inspect.currentframe().f_code.co_name)
        return 1

def test_IPCalculator_solve() -> int:
    try:
        attributes = {
            IPCalcAttributes.CDA: 0.195,
            IPCalcAttributes.AIRDENSITY: 1.12,
            IPCalcAttributes.MASSKG: 100,
            IPCalcAttributes.CRR: 0.002,
            IPCalcAttributes.MECHLOSSES: 0.02,
            IPCalcAttributes.DT: .1,
            IPCalcAttributes.POWERPLAN: [(0,500,1),
                                         (1,988,14),
                                         (15,550,20),
                                         (35,458,100),
                                         (135,523,120)]
        }
        ipc = IPCalculator(**attributes)
        ipc.solve()
        printSuccess(inspect.currentframe().f_code.co_name)
        return 0
    except:
        printFailure(inspect.currentframe().f_code.co_name)
        return 1

def test_IPCalculator_getSimResults() -> int:
    try:
        attributes = {
            IPCalcAttributes.CDA: 0.195,
            IPCalcAttributes.AIRDENSITY: 1.12,
            IPCalcAttributes.MASSKG: 100,
            IPCalcAttributes.CRR: 0.002,
            IPCalcAttributes.MECHLOSSES: 0.02,
            IPCalcAttributes.DT: .1,
            IPCalcAttributes.POWERPLAN: [(0,500,1),
                                         (1,988,14),
                                         (15,550,20),
                                         (35,458,100),
                                         (135,523,120)]
        }
        ipc = IPCalculator(**attributes)
        ipc.solve()
        frontendData = ipc.getSimResults()
        printSuccess(inspect.currentframe().f_code.co_name)
        return 0
    except:
        printFailure(inspect.currentframe().f_code.co_name)
        return 1

def test_CDACalculator() -> int:
    try:
        calc = CdACalculator("/Users/daviddomonoske/cs_projects/fit_file_testing/activity.fit",
                             0, 0, 0, 0)
        calc.readFitFile()

        plt.plot(calc.t, calc.v)
        plt.show()
        printSuccess(inspect.currentframe().f_code.co_name)
        return 0
    except:
        printFailure(inspect.currentframe().f_code.co_name)
        return 1

test_list = [test_IPCalculator_calcPedalForce,
             test_IPCalculator_solve,
             test_IPCalculator_getSimResults,
             test_CDACalculator]

# run all tests
def main():
    print("wottcalcs tests:")
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
