from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = ROOT / "docker-compose.yml"


class ComposeConfigTests(unittest.TestCase):
    def test_docker_compose_does_not_commit_default_postgres_password(self) -> None:
        compose = COMPOSE_FILE.read_text()

        self.assertNotIn("POSTGRES_PASSWORD:-", compose)


if __name__ == "__main__":
    unittest.main()
