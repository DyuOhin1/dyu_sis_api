from sis.connection import Connection


class ConnectionParser:
    @staticmethod
    def parse_connection(token: dict, is_icloud : bool) -> Connection:
        return Connection(
            student_id=token["s_id"],
            php_session_id=token["ic" if is_icloud else "sis"]["session_id"],
            last_login_timestamp=token["ic" if is_icloud else "sis"]["login_timestamp"]
        )