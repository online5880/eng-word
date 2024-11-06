# custom_logging.py

import json
import os
from datetime import datetime
import logging

class JsonArrayFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            with open(filename, 'w', encoding=encoding) as f:
                f.write('[\n')
        else:
            with open(filename, 'rb+') as f:
                f.seek(-2, os.SEEK_END)
                f.truncate()

    def emit(self, record):
        msg = self.format(record)
        try:
            with open(self.baseFilename, 'a', encoding=self.encoding) as f:
                if os.path.getsize(self.baseFilename) > 2:
                    f.write(',\n')
                f.write(msg)
                f.write('\n]')
        except Exception:
            self.handleError(record)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        if record.exc_info:
            log_data['traceback'] = self.formatException(record.exc_info)

        request = getattr(record, 'request', None)
        if request:
            log_data['http'] = {
                'method': request.method,
                'path': request.path,
                'status_code': getattr(record, 'status_code', None),
            }

        return json.dumps(log_data, ensure_ascii=False)
