import ast
import glob

ENTRYPOINT_DIR = "src/log_ingestor"


class InitConfigVisitor(ast.NodeVisitor):
    """
    Detecta llamadas a init_config() fuera del bloque:

        if __name__ == "__main__":
    """

    def __init__(self):
        self.inside_main = False
        self.offending = []

    def visit_If(self, node):
        """
        Detecta:
            if __name__ == "__main__":
        """
        is_main_block = (
            isinstance(node.test, ast.Compare)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "__name__"
            and len(node.test.ops) == 1
            and isinstance(node.test.ops[0], ast.Eq)
            and len(node.test.comparators) == 1
            and isinstance(node.test.comparators[0], ast.Constant)
            and node.test.comparators[0].value == "__main__"
        )
        previous_state = self.inside_main

        if is_main_block:
            self.inside_main = True

        for stmt in node.body:
            self.visit(stmt)

        self.inside_main = previous_state
        for stmt in node.orelse:
            self.visit(stmt)

    def visit_Call(self, node):
        """
        Detecta llamadas:
            init_config()
        """

        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "init_config"
        ):
            if not self.inside_main:
                self.offending.append(
                    (
                        self.current_file,
                        f"line {node.lineno}: init_config()"
                    )
                )

        self.generic_visit(node)


def test_init_config_calls_are_in_main_block():
    """
    Verifica que init_config() únicamente se invoque
    dentro de:

        if __name__ == "__main__":
    """

    files = glob.glob(f"{ENTRYPOINT_DIR}/*.py")

    offending = []

    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=fp)
        visitor = InitConfigVisitor()
        visitor.current_file = fp
        visitor.visit(tree)
        offending.extend(visitor.offending)

    assert not offending, (
        "init_config() found outside __main__ blocks:\n"
        + "\n".join(
            f"{fp} -> {detail}"
            for fp, detail in offending
        )
    )
