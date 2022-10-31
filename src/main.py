import sys
from typing import List

import parser


def main(args: List[str]):
    match len(args):
        case 0:
            print('Missing 1 argument: path to the words file')
            return
        case 1:
            pass
        case _:
            print('Ignoring arguments: "{}"'.format('", "'.join(args[1:])))

    try:
        words = parser.parse_words_file(args[0])
    except parser.ParserError as e:
        print(e)
        return


if __name__ == '__main__':
    main(sys.argv[1:])
