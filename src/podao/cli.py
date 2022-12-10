import click

from podao.constant import ALL_GROUP_NAME
from podao.main import Project
from podao.util import check_pyenv, check_pyvenv


'''
TODO: 
    1. src/<package>
    2. .vscode/settings.json, --editor / --ide
'''


@click.group
def pd():
    pass


@pd.command
@click.argument('dir', nargs=1)
@click.argument('python', nargs=1, required=False)
@click.option(
    '-ide',
    '-i',
    type=click.Choice(['vscode'], case_sensitive=False),
    help='Generate IDE configuation file.',
)
def init(dir, python, ide=None):
    '''
    Init project enviorment. E.g.\n
    pd init . 3.10.4
    '''
    if v := check_pyenv():
        click.secho(f'Using {v}', bold=True)
    else:
        click.secho('Warning: Cannot find pyenv, install it firstly!', fg='red', err=True)
        return

    if check_pyvenv():
        click.secho(f'Warning: Project environment already existed', fg='red', err=True)
        return

    try:
        pro = Project(dir)
        for s in pro.create_venv(python):
            click.secho(s)

        for s in pro.create_structure(ide):
            click.secho(s)
    except Exception as e:
        click.secho(e, fg='red', err=True)
    else:
        click.secho(f'Successfully initialize virtual environment')


@pd.command
@click.argument('packages', nargs=-1)
@click.option(
    '--dev', '-d', is_flag=True, default=False, help='Add packages to dev dependencies'
)
@click.option(
    '--group',
    '-g',
    prompt=True,
    prompt_required=False,
    default='',
    help='Add packages to a specific group default ``.',
)
def install(dev, group, packages):
    '''
    Install packages and add to specific group in pyproject.toml. \n
    Beware using quotes around specifiers in the shell when using >, <.  E.g.\n
    pd install 'requests<3.0.0,>=2.19.1'
    '''
    if root := check_pyvenv():
        click.secho(f'Working on {root}')
    else:
        click.secho(
            'Warning: Cannot find virtual environment, init it firstly using `pd init dir [python version]`',
            fg='red',
            err=True,
        )

    if dev:
        group = 'dev'

    try:
        pro = Project(root)
        for s in pro.install(packages, group):
            click.secho(s)

    except Exception as e:
        click.secho(e, fg='red', err=True)
    else:
        click.secho(
            f'Successfully added {" ".join(packages)} to {(group + " of optional-") if group else ""}dependencies'
        )


@pd.command
@click.argument('packages', nargs=-1)
def uninstall(packages):
    '''
    Uninstall packages and remove from the group in pyproject.toml. E.g.\n
    pd uninstall requests
    '''
    if root := check_pyvenv():
        click.secho(f'Working on {root}')
    else:
        click.secho(
            'Warning: Cannot find virtual environment, init it firstly using `pd init dir [python version]`',
            fg='red',
            err=True,
        )

    if not click.confirm(f'Do you want to remove {" ".join(packages)}'):
        return

    try:
        pro = Project(root)
        for s in pro.uninstall(packages):
            click.secho(s)

    except Exception as e:
        click.secho(e, fg='red', err=True)
    else:
        click.secho(f'Successfully remove {" ".join(packages)} dependencies')


@pd.command
@click.option(
    '--dev', '-d', is_flag=True, default=False, help='Take dev packages snapshot'
)
@click.option(
    '--all', '-a', is_flag=True, default=False, help='Take all packages snapshot'
)
@click.option(
    '--group',
    '-g',
    prompt=True,
    prompt_required=False,
    default='',
    help='Take a group packages snapshot default `main`',
)
def freeze(dev, group, all):
    '''
    Create a environment packages snapshot to requirements.txt file. E.g.\n
    pd freeze
    '''
    if root := check_pyvenv():
        click.secho(f'Working on {root}')
    else:
        click.secho(
            'Warning: Cannot find virtual environment, init it firstly using `pd init dir [python version]`',
            fg='red',
            err=True,
        )

    if all:
        group = ALL_GROUP_NAME
    if dev:
        group = 'dev'

    try:
        pro = Project(root)
        for s in pro.freeze(group):
            click.secho(s)

    except Exception as e:
        click.secho(e, fg='red', err=True)
    else:
        click.secho('Done!')
