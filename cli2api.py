"""
Note that part of the code is from https://github.com/yt-dlp/yt-dlp/blob/master/devscripts/cli_to_api.py
Last commit was at Aug 7, 2025
"""
# Allow direct execution
import yt_dlp
import yt_dlp.options
from shlex import split as shlex_split  # shlex로 처리해도 딱히 결과에 문제는 없었음
from pprint import pformat
from rich.pretty import pprint, Pretty

_create_parser = yt_dlp.options.create_parser


def _parse_patched_options(opts):
    patched_parser = _create_parser()
    patched_parser.defaults.update({
        'ignoreerrors': False,
        'retries': 0,
        'fragment_retries': 0,
        'extract_flat': False,
        'concat_playlist': 'never',
        'update_self': False,
    })
    yt_dlp.options.create_parser = lambda: patched_parser
    try:
        return yt_dlp.parse_options(opts)
    finally:
        yt_dlp.options.create_parser = _create_parser


_default_opts = _parse_patched_options([]).ydl_opts


def _cli_to_api(opts, cli_defaults=False):
    opts = (yt_dlp.parse_options if cli_defaults else _parse_patched_options)(
        opts).ydl_opts

    diff = {k: v for k, v in opts.items() if _default_opts[k] != v}
    if 'postprocessors' in diff:
        diff['postprocessors'] = [pp for pp in diff['postprocessors']
                                  if pp not in _default_opts['postprocessors']]
    return diff


def parse_cli_args(cli_args: str, cli_defaults=False) -> dict[str, object]:
    """
    Args:
        args: A string of CLI arguments, e.g. "yt-dlp --format "bv[height<=720]+ba" --output '%(title)s.%(ext)s' URL". 'yt-dlp' can be omitted.
    Returns:
        A dictionary of API options that correspond to the given CLI arguments, e.g. {'format': 'bv[height<=720]+ba', 'output': '%(title)s.%(ext)s'}.
    """
    if not cli_args.startswith('yt-dlp '):
        cli_args = 'yt-dlp ' + cli_args
    api = _cli_to_api(shlex_split(cli_args), cli_defaults=cli_defaults)
    return api


if __name__ == "__main__":

    opts = input(">>> yt-dlp ")
    api_opts = parse_cli_args(opts)
    pprint(api_opts)