from config import get_app
from output import display
from argparse import ArgumentParser


def validate():
    app = get_app(options.input)
    app.validate()
    display(app.results)


def run():
    parser = ArgumentParser()

    # TODO: Enable arguments when relevant functionality is added
    # parser.add_argument('command', help='validate app urls against configured checks', default='validate', choices=[
    #     'validate'
    # ])
    parser.add_argument('-i', '--input', help='app configuration file path')

    global options
    options = parser.parse_args()

    switcher = {
        None: lambda: parser.print_help(),
        'validate': lambda: validate()
    }
    func = switcher.get(getattr(options, 'command', 'validate' if options.input else None), lambda: None)
    if func:
        func()


if __name__ == '__main__':
    run()
