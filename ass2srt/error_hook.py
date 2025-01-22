
import sys
import traceback

def custom_excepthook(exc_type, exc_value, exc_traceback):
    with open('error.log', 'a', encoding='utf-8') as f:
        f.write(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = custom_excepthook
