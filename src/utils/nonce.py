import time
import uuid
from typing import Set
from datetime import datetime, timedelta

class NonceManager:
    def __init__(self):
        self._used_nonces: Set[tuple[str, float]] = set()
        self._nonce_timeout = 3600  # 1 hour
        
    def generate_nonce(self) -> str:
        return str(uuid.uuid4())
        
    def validate_nonce(self, nonce: str) -> bool:
        current_time = time.time()
        
        # 清理過期的 nonce
        self._used_nonces = {
            (n, t) for n, t in self._used_nonces 
            if current_time - t < self._nonce_timeout
        }
        
        # 檢查 nonce 是否已使用
        for used_nonce, _ in self._used_nonces:
            if used_nonce == nonce:
                return False
                
        # 儲存新的 nonce
        self._used_nonces.add((nonce, current_time))
        return True 