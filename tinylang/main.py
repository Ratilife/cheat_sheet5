import sys
from antlr4 import FileStream, CommonTokenStream
from TinyLangLexer import TinyLangLexer
from TinyLangParser import TinyLangParser


def print_tokens(path: str) -> None:
    input_stream = FileStream(path, encoding="utf-8")
    lexer = TinyLangLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    token_stream.fill()
    for token in token_stream.tokens:
        token_name = lexer.symbolicNames[token.type] if token.type >= 0 else str(token.type)
        print(f"{token.line}:{token.column}\t{token_name}\t{token.text}")


def parse_file(path: str) -> None:
    input_stream = FileStream(path, encoding="utf-8")
    lexer = TinyLangLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = TinyLangParser(stream)
    tree = parser.program()
    print("\nParse tree:")
    print(tree.toStringTree(recog=parser))


if __name__ == "__main__":
    src_path = sys.argv[1] if len(sys.argv) > 1 else "examples/hello.tiny"
    print(f"Lexing tokens from: {src_path}\n")
    print_tokens(src_path)
    parse_file(src_path)