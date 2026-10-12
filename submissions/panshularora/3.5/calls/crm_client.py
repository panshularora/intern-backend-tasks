import logging
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class CRMClient:
    BASE_URL = "https://jsonplaceholder.typicode.com"

    def __init__(self, timeout: int = 10):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        self.timeout = timeout

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(requests.exceptions.ConnectionError),
    )
    def get_users(self) -> list[dict]:
        response = self.session.get(f"{self.BASE_URL}/users", timeout=self.timeout)
        return self._handle_response(response)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def get_user(self, user_id: int) -> dict:
        if user_id <= 0:
            raise ValueError("user_id must be greater than 0")
        response = self.session.get(f"{self.BASE_URL}/users/{user_id}", timeout=self.timeout)
        return self._handle_response(response)

    def create_post(self, title: str, body: str, user_id: int) -> dict:
        if not title or not body:
            raise ValueError("title and body are required")
        if user_id <= 0:
            raise ValueError("user_id must be greater than 0")
        response = self.session.post(
            f"{self.BASE_URL}/posts",
            json={'title': title, 'body': body, 'userId': user_id},
            timeout=self.timeout,
        )
        return self._handle_response(response)

    def _handle_response(self, response: requests.Response):
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error: %s | Response: %s", e, response.text)
            raise
        except ValueError:
            logger.error("Invalid JSON response: %s", response.text)
            raise
