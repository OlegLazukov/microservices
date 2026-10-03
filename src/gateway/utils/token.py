from fastapi import Request


class Token:
    def extract_token(self, request: Request) -> str | None:
        auth = request.headers.get("Authorization", "")
        parts = auth.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        return None