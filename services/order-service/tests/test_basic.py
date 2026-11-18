
"""
Testes básicos do order-service.

Valida o ambiente inicial de testes sem acessar
recursos externos da OCI.
"""

def test_python_version():
    """Verifica se a execução utiliza Python 3.11."""
    import sys

    assert sys.version_info[:2] == (3, 11)