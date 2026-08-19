
class TestCase:
    __test__ = False

    def __init__(
        self,
        test_case_id: int,
        problem_id: int,
        input_data: str,
        expected_output: str,
        is_hidden: bool = False,
    ):
        self.test_case_id = test_case_id
        self.problem_id = problem_id
        self.input_data = input_data
        self.expected_output = expected_output
        self.is_hidden = is_hidden
