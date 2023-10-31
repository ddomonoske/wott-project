import customtkinter as ctk
from wottmodel import *
from wottview import *
from wottcontroller import *
from test_helpers import *

def test_Controller_replaceEmptyName() -> int:
    try:
        newStrs = Controller.replaceEmptyName(riderStr)
        for nameID in newStrs:
            if nameID[0] == "":
                raise Exception
        printSuccess("test_Controller_replaceEmptyName")
        return 0
    except:
        printFailure("test_Controller_replaceEmptyName")
        return 1

test_list = [
    test_Controller_replaceEmptyName
]

# run all tests
def main():
    # run the non-GUI tests
    failedTests = 0
    for test in test_list:
        if test():
            failedTests += 1

    if failedTests:
        printFailure(f"{bcolors.EMPH}\n{failedTests} test(s) failed")
        printSuccess(f"{bcolors.EMPH}{len(test_list)-failedTests} test(s) passed")
    else:
        printSuccess(f"{bcolors.EMPH}\nAll {len(test_list)} tests passed")

    # run the GUI test
    ctk.set_default_color_theme("blue")
    ctk.set_appearance_mode("system")
    app = ctk.CTk()
    app.wm_state("zoomed")
    app.grid_columnconfigure(0,weight=1)
    app.grid_rowconfigure(0,weight=1)

    testDirectory = Path.cwd() / "wott_testcontroller_main"
    model = Model(str(testDirectory))
    view = View(app)
    controller = Controller(model, view)

    view.setController(controller)

    view.grid(row=0, column=0, sticky="NSEW")

    app.mainloop()

     # delete file and directory
    testDirectory.rmdir()

if __name__ == '__main__':
    main()
