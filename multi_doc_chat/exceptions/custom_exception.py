import sys
import traceback
from typing import Optional

class CustomException(Exception):
    def __init__(self, error_message, error_details: Optional[object] = None):
        # Normalize message
        norm_msg = str(error_message)

        # Resolve exc_info
        exc_type = exc_value = exc_tb = None
        if error_details is None:
            exc_type, exc_value, exc_tb = sys.exc_info()
        else:
            if hasattr(error_details, "exc_info") and callable(getattr(error_details, "exc_info")):
                exc_type, exc_value, exc_tb = error_details.exc_info()
            elif isinstance(error_details, BaseException):
                exc_type, exc_value, exc_tb = type(error_details), error_details, error_details.__traceback__
            else:
                exc_type, exc_value, exc_tb = sys.exc_info()

        # Walk to last traceback
        last_tb = exc_tb
        while last_tb and last_tb.tb_next:
            last_tb = last_tb.tb_next

        self.file_name = last_tb.tb_frame.f_code.co_filename if last_tb else "unknown"
        self.lineno = last_tb.tb_lineno if last_tb else -1
        self.error_message = norm_msg

        if exc_type and exc_tb:
            self.traceback_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        else:
            self.traceback_str = ""

        super().__init__(self.__str__())

    def __str__(self):
        base = f"Error in [{self.file_name}] at line [{self.lineno}] | Message: {self.error_message}"
        if self.traceback_str:
            return f"{base}\nTraceback:\n{self.traceback_str}"
        return base

    def __repr__(self):
        return f"CustomException(file={self.file_name!r}, line={self.lineno}, message={self.error_message!r})"

if __name__ == "__main__":
    try: 
        1 / 0 
    except Exception as e:
        ce = CustomException("Division Failed", e) 
        print(str(ce))
        raise ce