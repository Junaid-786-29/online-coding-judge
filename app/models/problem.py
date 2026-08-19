class Problem:

    def __init__(
        self,
        problem_id: int,
        title: str,
        description: str,
        difficulty: str,
        constraints: str | None = None,
        input_format: str | None = None,
        output_format: str | None = None,
    ):
        self.problem_id = problem_id
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.constraints = constraints
        self.input_format = input_format
        self.output_format = output_format

