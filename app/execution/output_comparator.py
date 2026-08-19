

def normalize_output(output: str) -> str:
    """
    Normalize output string for comparison:
    1. Standardize line endings (\r\n and \r to \n).
    2. Strip trailing whitespace from each line.
    3. Strip overall leading and trailing whitespace.
    """
    if output is None:
        return ""

    normalized = output.replace("\r\n", "\n").replace("\r", "\n")

    lines = [line.rstrip() for line in normalized.split("\n")]
    
    result = "\n".join(lines).strip()
    return result


def compare_output(actual: str, expected: str) -> bool:
    """
    Compare actual program output against expected output after normalization.
    """
    return normalize_output(actual) == normalize_output(expected)
