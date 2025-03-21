import unittest
from src.transformer import shittify_code

class TestShittier(unittest.TestCase):
    def test_shittier(self):
        code = "print('Hello, world!')"
        obfuscated = shittify_code(code)
        self.assertNotEqual(code, obfuscated)
        self.assertIn("print", obfuscated)

if __name__ == "__main__":
    unittest.main()
