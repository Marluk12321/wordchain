import time
import sys
from typing import List

import wordchain.generators as generators
import wordchain.graph as graph
import wordchain.parser as parser


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

    word_graph = graph.Graph(words)
    generator = generators.RandomGenerator(repeats=10000)
    start_time = time.time()
    chain = generator.generate(word_graph)
    end_time = time.time()
    assert len(chain) == len(frozenset(chain))
    print(f'Finished in {end_time - start_time}s\n'
          f'Chain length: {len(chain)}', end='\n\n')

    while True:
        match input('Display words from chain? (y/n): ').strip().lower():
            case 'y':
                print('\n'.join(chain))
                break
            case 'n':
                break
            case _:
                continue


if __name__ == '__main__':
    main(sys.argv[1:])
