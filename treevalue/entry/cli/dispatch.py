import click

from .base import CONTEXT_SETTINGS, print_version


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Show package's version information.")
def treevalue_cli():
    pass
