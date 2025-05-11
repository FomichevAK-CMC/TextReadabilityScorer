# -*- coding: utf-8 -*-
from ru_analyzer import *
import tester
import sys


def draw_table(labels: List[str], *col_values):
    ncols = len(labels)
    nrows = len(col_values[0])
    widths = [max(len(labels[c]), max(len(str(val)) for val in col_values[c])) + 2 for c in range(ncols)]
    print('╔' + '╤'.join(f'{f"╡{labels[i]}╞":═^{widths[i]}}' for i in range(ncols)) + '╗')
    for r in range(nrows):
        print('║' + '┼'.join(f'{col_values[c][r]:^{widths[c]}}' for c in range(ncols)) + '║')
    print('╚' + '╧'.join(f'{"═"*widths[i]}' for i in range(ncols)) + '╝')


def display_base_stats(ra: RUAnalyzer):
    stat_names = [
        "Предложений",
        "Слов",
        "Слогов",
        "Букв",
        "Цифр"
    ]
    stat_values = [
        ra.sent_count(),
        ra.ru_word_count(),
        ra.ru_syl_count(),
        ra.ru_let_count(),
        ra.dig_count()
    ]

    draw_table(
        ['Статистика', 'Значение'],
        stat_names,
        stat_values
    )


def display_additional_stats(ra: RUAnalyzer):
    avr_names = [
        'Слов в предложении',
        'Слогов в слове',
        'Букв в слове',
        'Предложений на 100 слов'
    ]
    avr_values = [
        f'{ra.avr_word_per_sent(): .2f}',
        f'{ra.ru_syl_count() / ra.ru_word_count():.2f}',
        f'{ra.ru_let_count() / ra.ru_word_count():.2f}',
        f'{100 / ra.avr_word_per_sent():.2f}',
    ]

    draw_table(
        ['Среднее кол-во', 'Значение'],
        avr_names,
        avr_values
    )


def main():
    encoding = ''
    if len(sys.argv) == 1:
        filename = str(input("Введите имя текстового файла для анализа:\n"))
        if not filename:
            raise Exception("No text file specified!")
        encoding = str(input("Введите кодировку файла (пустота=windows-1251):\n"))
    elif sys.argv[1] == "-f":
        filename = sys.argv[2]
        if len(sys.argv) > 3:
            encoding = sys.argv[3]
    elif sys.argv[1] == "-t":
        tester.test()
        exit()
    else:
        print(sys.argv[1])
        raise Exception("No text file specified!")

    with open(filename, 'r', encoding=encoding if encoding else 'windows-1251') as f:
        ra = RUAnalyzer(f)

    ind_names = ['FRES', 'FKGL', 'CLI', 'ARI']
    indexes = [ra.FRES(), ra.FKGL(), ra.ARI(), ra.CLI()]
    draw_table(
        ['Индекс', 'Значение', 'Уровень'],
        ind_names,
        [f'{ind: .3f}' for ind in indexes],
        [interp(*ind) for ind in zip(ind_names, indexes)]
    )
    
    display_base_stats(ra)
    """
    display_additional_stats(ra)
    print('\n')

    print('Наиболее значимые предложения для индексов:')
    most = {
        'FRES': (t := min(ra.sentences(), key=lambda s: RUAnalyzer(s).FRES()), RUAnalyzer(t).FRES()),
        'FKGL': (t := max(ra.sentences(), key=lambda s: RUAnalyzer(s).FKGL()), RUAnalyzer(t).FKGL()),
        'CLI': (t := max(ra.sentences(), key=lambda s: RUAnalyzer(s).CLI()), RUAnalyzer(t).CLI()),
        'ARI': (t := max(ra.sentences(), key=lambda s: RUAnalyzer(s).ARI()), RUAnalyzer(t).ARI())
    }
    for ind in most:
        print(f'{ind}: {most[ind][1]:.2f}')
        print(most[ind][0].join('').strip())
        display_base_stats(RUAnalyzer(most[ind][0]))
        display_additional_stats(RUAnalyzer(most[ind][0]))
        print()
    """
    
if __name__ == '__main__':
    """
    Command line arguments:
        -f <path_to_file> [<encoding>] - passes specified file and encoding (windows-1251 if not specified) to the analyzer.
        -t - runs tests.
        If no parameters are specified - prompts user to input filename and encoding.
    """
    main()

