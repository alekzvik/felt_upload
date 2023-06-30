from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Generator, List, Optional

import requests
import typer
from rich.console import Group
from rich.live import Live
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from typing_extensions import Annotated

from felt_upload.api import Felt, UnauthorizedError

app = typer.Typer(no_args_is_help=True)


class Basemap(str, Enum):
    default = "default"
    satellite = "satellite"


talk = print

download_progress = Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
    DownloadColumn(),
    transient=True,
)
task_progress = Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    transient=True,
)
group = Group(
    task_progress,
    download_progress,
)


@contextmanager
def catch_unauthorized() -> Generator[None, None, None]:
    try:
        yield
    except UnauthorizedError:
        raise typer.BadParameter(
            "[401 Unauthorized] Token is either invalid or you have insufficient permissions.",
            param_hint="--token",
        )


@contextmanager
def spinner(title: str) -> Generator[None, None, None]:
    task_id = task_progress.add_task(title)
    yield
    task_progress.remove_task(task_id)


@app.callback()
def init(
    ctx: typer.Context,
) -> None:
    """Felt CLI upload tool."""
    ctx.ensure_object(dict)
    ctx.obj["live"] = ctx.with_resource(Live(group, transient=True))
    ctx.obj["session"] = requests.Session()


@app.command()
def user(
    ctx: typer.Context,
    token: Annotated[str, typer.Option(envvar="FELT_TOKEN")],
) -> None:
    """Display current user.

    Useful to validate the token."""
    task_progress.add_task("Fetching user")
    felt_api = Felt(token, session=ctx.obj["session"])
    with catch_unauthorized():
        user = felt_api.user()
    talk(f"Current user: {user['name']} <{user['email']}>")


@app.command()
def map(
    ctx: typer.Context,
    token: Annotated[str, typer.Option(envvar="FELT_TOKEN")],
    title: Optional[str] = None,
    layer_name: Optional[str] = None,
    basemap: Optional[Basemap] = None,
    zoom: Optional[float] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    layer_url: Optional[List[str]] = None,  # TODO: consider yarl to validate
    files: Annotated[
        Optional[List[Path]],
        typer.Argument(
            ...,
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
        ),
    ] = None,
    silent: Annotated[
        bool, typer.Option("--silent", help="Write only necessary output")
    ] = False,
) -> None:
    """Create a map with optional single layer."""
    if files and layer_url:
        raise typer.BadParameter(
            "Only one is allowed", param_hint="[FILES]... or --layer_url"
        )

    with spinner("Creating a map..."):
        felt_api = Felt(token, session=ctx.obj["session"])
        with catch_unauthorized():
            map = felt_api.create_map(
                title=title, basemap=basemap, zoom=zoom, lat=lat, lon=lon
            )
            map_id = map["id"]

    if not silent:
        talk(f"Map created.\nid: {map['id']}\nurl: {map['url']}\n")

    if files:
        layer(ctx, token=token, map_id=map_id, name=layer_name, files=files)

    if layer_url:
        layer_import(
            ctx, token=token, map_id=map_id, name=layer_name, layer_urls=layer_url
        )

    if silent:
        talk(map["id"])


@app.command()
def layer(
    ctx: typer.Context,
    token: Annotated[str, typer.Option(envvar="FELT_TOKEN")],
    map_id: str,
    files: Annotated[
        List[Path],
        typer.Argument(
            ...,
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
        ),
    ],
    name: Optional[str] = None,
    silent: Annotated[
        bool, typer.Option("--silent", help="Write only necessary output")
    ] = False,
) -> None:
    """Add layer to existing map."""
    with spinner("Adding a layer..."):
        felt_api = Felt(token, session=ctx.obj["session"])

        task_map = {}
        for file in files:
            task_id = download_progress.add_task(file.name)
            task_map[file.name] = task_id

        def update_file_progress(filename: str, completed: int, total: int) -> None:
            download_progress.update(
                task_map[filename], completed=completed, total=total
            )

        with catch_unauthorized():
            layer = felt_api.create_layer(
                map_id,
                files,
                name=name,
                update_file_progress=update_file_progress,
            )
    if not silent:
        talk(f"Layer added.\nid: {layer['id']}\n")


@app.command()
def layer_import(
    ctx: typer.Context,
    token: Annotated[str, typer.Option(envvar="FELT_TOKEN")],
    map_id: str,
    layer_urls: List[str],
    name: Optional[str] = None,
    silent: Annotated[
        bool, typer.Option("--silent", help="Write only necessary output")
    ] = False,
) -> None:
    """Import layer from url to existing map."""
    with spinner("Importing a layer..."):
        felt_api = Felt(token, session=ctx.obj["session"])

        with catch_unauthorized():
            for url in layer_urls:
                layer = felt_api.import_layer(
                    map_id,
                    url,
                    name=name,
                )

    # TODO: return id for every file uploaded
    if not silent:
        talk(f"Layer added.\nid: {layer['id']}\n")
