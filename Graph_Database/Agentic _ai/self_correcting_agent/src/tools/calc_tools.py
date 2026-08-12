def python_calculator(expression: str) -> str:
    try:
        allowed_chars = "0123456789+-*/(). "
        if all(c in allowed_chars for c in expression):
            return str(eval(expression))
        return "Error: Invalid characters in expression."
    except Exception as e:
        return f"Execution error: {str(e)}"
