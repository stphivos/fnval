import sys
import colorama
from colorama import Fore, Back, Style
from itertools import groupby

colorama.init()


def sort_results(results):
    return sorted(results, key=lambda x: (x.url, x.method))


def format_result(result):
    return Style.RESET_ALL + result.test + (
        Fore.RED + ' ({0}) => FAILED, {1}'.format(result.status_code, result.fault) if result.is_error else
        Fore.GREEN + ' ({0}) => OK'.format(result.status_code)
    ) + Style.RESET_ALL


def display_outcome(has_errors):
    if has_errors:
        sys.exit(Fore.RED +
                 'One or more functions have produced unexpected results...' +
                 Style.RESET_ALL if has_errors else None)
    else:
        print Fore.GREEN + 'All functions have produced the expected result!' + Style.RESET_ALL
        sys.exit()


def display(results):
    results = sort_results(results)

    for url, u_group in groupby(results, lambda x: x.url):
        print url
        for method, m_group in groupby(u_group, lambda x: x.method):
            print ' {0}'.format(method)
            for r in m_group:
                print '     {0}'.format(format_result(r))
        print ''

    display_outcome(len([r for r in results if r.is_error]))


class Result:
    def __init__(self, url, method, test):
        self.url = url
        self.method = method
        self.test = test
        self.is_error = None
        self.response = None

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def fault(self):
        return self.response.content[0:100] if self.response.content else 'Empty body'
