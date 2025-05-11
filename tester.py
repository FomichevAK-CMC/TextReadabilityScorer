# -*- coding: utf8 -*-
import ru_analyzer
ru_an_path = 'tests/ru_analyzer_tests'

test_types = {
    "token_words": [1, 2],
    "token_numbers": [3],
    "sentences": [4],
    "index": [5, 6]
}

def test():
    for test_type, indexes in test_types.items():
        print(f"Test type: {test_type}")
        for i in indexes:
            with open(f'tests/ru_analyzer_tests/test_{i}/in.txt', encoding='windows-1251') as f:
                ra = ru_analyzer.RUAnalyzer(f)
            with open(f'tests/ru_analyzer_tests/test_{i}/out.txt', encoding='windows-1251') as f:
                ans = f.read().strip().split('\n')
            match test_type:
                case "token_words":
                    res = list(map(str, ra.ru_words()))
                case "token_numbers":
                    res = list(map(str, ra.numbers() + [f'DIGITS:{ra.dig_count()}']))
                case "sentences":
                    res = [repr(s.join('_')) for s in ra.sentences()]
                case "index":
                    res = [f"FRES:{ra.FRES():.5f}",
                           f"CLI:{ra.CLI():.5f}",
                           f"FKGL:{ra.FKGL():.5f}",
                           f"ARI:{ra.ARI():.5f}"
                    ]
            print(f"Test {i}:", "OK" if res == ans else 'FAILED')
