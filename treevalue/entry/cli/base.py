import click
from click.core import Context, Option

from ...config.meta import __TITLE__, __VERSION__, __AUTHOR__, __AUTHOR_EMAIL__

_raw_authors = [item.strip() for item in __AUTHOR__.split(',') if item.strip()]
_raw_emails = [item.strip() for item in __AUTHOR_EMAIL__.split(',')]
if len(_raw_emails) < len(_raw_authors):
    _raw_emails += [None] * (len(_raw_authors) - len(_raw_emails))
elif len(_raw_emails) > len(_raw_authors):
    _raw_emails[len(_raw_authors) - 1] = tuple(_raw_emails[len(_raw_authors) - 1:])
    del _raw_emails[len(_raw_authors):]

_author_tuples = [
    (author, tuple([item for item in (email if isinstance(email, tuple) else ((email,) if email else ())) if item]))
    for author, email in zip(_raw_authors, _raw_emails)
]
_authors = [
    author if not emails else '{author} ({emails})'.format(author=author, emails=', '.join(emails))
    for author, emails in _author_tuples
]


# noinspection PyUnusedLocal
def print_version(ctx: Context, param: Option, value: bool) -> None:
    """
    Print version information of cli
    :param ctx: click context
    :param param: current parameter's metadata
    :param value: value of current parameter
    """
    if not value or ctx.resilient_parsing:
        return
    click.echo('{title}, version {version}.'.format(title=__TITLE__.capitalize(), version=__VERSION__))
    if _authors:
        click.echo('Developed by {authors}.'.format(authors=', '.join(_authors)))
    ctx.exit()


CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Show package's version information.")
def _base_treevalue_cli():
    pass
