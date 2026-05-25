import unittest

from app.services.judge import Judge0Client, TestCaseInput, calculate_score, SubmissionResult


class FakeResponse:
    status_code = 201

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return [{"token": "token-1"}]


class FakeHttpClient:
    def __init__(self) -> None:
        self.last_json = None

    async def post(self, *args, **kwargs):
        self.last_json = kwargs["json"]
        return FakeResponse()


class Judge0ClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_submit_batch_converts_memory_limit_mb_to_kb(self) -> None:
        client = Judge0Client()
        fake_client = FakeHttpClient()
        client.client = fake_client

        tokens = await client.submit_batch(
            source_code="print(input())",
            language_id=71,
            test_cases=[TestCaseInput(stdin="hello\n", expected_output="hello\n")],
            time_limit=2.0,
            memory_limit=256,
        )

        self.assertEqual(tokens, "token-1")
        submission = fake_client.last_json["submissions"][0]
        self.assertEqual(submission["memory_limit"], 256 * 1024)
        self.assertEqual(submission["cpu_time_limit"], 2.0)

    def test_calculate_score_uses_all_or_nothing_mvp_policy(self) -> None:
        accepted = SubmissionResult(
            status_id=3,
            status_desc="Accepted",
            time=0.01,
            memory=1000,
            stdout="",
            stderr="",
        )
        wrong = SubmissionResult(
            status_id=4,
            status_desc="Wrong Answer",
            time=0.01,
            memory=1000,
            stdout="",
            stderr="",
        )

        self.assertEqual(calculate_score([accepted, accepted]), (2, 2, 100))
        self.assertEqual(calculate_score([accepted, wrong]), (2, 1, 0))
        self.assertEqual(calculate_score([]), (0, 0, None))


if __name__ == "__main__":
    unittest.main()
