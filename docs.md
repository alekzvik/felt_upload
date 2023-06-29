# `felt-upload`

Felt CLI upload tool.

**Usage**:

```console
$ felt-upload [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `layer`: Add layer to existing map.
* `layer-import`: Import layer from url to existing map.
* `map`: Create a map with optional single layer.
* `user`: Display current user.

## `felt-upload layer`

Add layer to existing map.

**Usage**:

```console
$ felt-upload layer [OPTIONS] MAP_ID FILES...
```

**Arguments**:

* `MAP_ID`: [required]
* `FILES...`: [required]

**Options**:

* `--token TEXT`: [env var: FELT_TOKEN; required]
* `--name TEXT`
* `--silent`: Write only necessary output
* `--help`: Show this message and exit.

## `felt-upload layer-import`

Import layer from url to existing map.

**Usage**:

```console
$ felt-upload layer-import [OPTIONS] MAP_ID LAYER_URLS...
```

**Arguments**:

* `MAP_ID`: [required]
* `LAYER_URLS...`: [required]

**Options**:

* `--token TEXT`: [env var: FELT_TOKEN; required]
* `--name TEXT`
* `--silent`: Write only necessary output
* `--help`: Show this message and exit.

## `felt-upload map`

Create a map with optional single layer.

**Usage**:

```console
$ felt-upload map [OPTIONS] [FILES]...
```

**Arguments**:

* `[FILES]...`

**Options**:

* `--token TEXT`: [env var: FELT_TOKEN; required]
* `--title TEXT`
* `--layer-name TEXT`
* `--basemap [default|satellite]`
* `--zoom FLOAT`
* `--lat FLOAT`
* `--lon FLOAT`
* `--layer-url TEXT`
* `--silent`: Write only necessary output
* `--help`: Show this message and exit.

## `felt-upload user`

Display current user.

Useful to validate the token.

**Usage**:

```console
$ felt-upload user [OPTIONS]
```

**Options**:

* `--token TEXT`: [env var: FELT_TOKEN; required]
* `--help`: Show this message and exit.
