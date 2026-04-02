import logging
import traceback

x = 1
try:
    print(x / 0)
except Exception:
    # print("Unexpected error:", sys.exc_info()[0])
    logging.error(traceback.format_exc())

print("done")
