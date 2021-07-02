from typing import List, Dict


class IJMeterTest:
    def run(
        self,
        args: List[str],
        test: str,
        files: List,
        serverless_provider: str,
        function_url: str or Dict[str, str],
        ts: float,
    ) -> str or None:
        """Load in the file for extracting text."""
        pass

    def plot(
        self,
        test_number: str,
        files: List,
        execution_time: str,
        colors: List[str],
        result_path: str,
        serverless_provider: str,
        ts: float,
    ):
        """Extract text from the currently loaded file."""
        pass
