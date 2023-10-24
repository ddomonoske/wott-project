fruitStr = [("apple", 1),
            ("banana", 2),
            ("cherry", 5),
            ("dragon fruit", 4),
            ("elderberry", 3),
            ("fig", 90),
            ("grapes", 12)]

riderStr = [("David", 0),
            ("Anders", 2),
            ("Grant", 4),
            ("Brendan", 6),
            ("Colby", 8),
            ("Viggo", 10),
            ("Eddy", 12),
            (" ", 13)]

envirStr = [("LA", 10),
            ("COS", 9),
            ("San Juan", 8),
            ("Paris", 7)]

simStr = [("10/8/23 COS Testing", 2),
          ("8/8/23 Worlds", 4)]

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
