# felt-upload

## What
[Felt](http://felt.com) is "the best way to work with maps, together".

And this is a simple CLI application to upload your files to it from your console.

## Why
The Felt API is pretty straightforward, but sometimes you just need a tool to upload a file from a command line and not deal with all the insides.

## Install
```
pip install felt-upload
```
or you can use [pipx](https://pypa.github.io/pipx/):
```
pipx install felt-upload
```

## API Token
To use it you need an API token from Felt. Get yours [here](https://felt.com/users/integrations).
You can either pass it directly as `--token` option or provide as an env variable `FELT_TOKEN`.
You can check token with the `user` command, which will print out a user for the given token.
```bash
export FELT_TOKEN="felt_pat_Ul8HIuHJZuMyxJJ7ZHajj3gBM6KAs4mnnE6f7GiJIPC"
felt-upload user
```
```bash
felt-upload user --token "felt_pat_Ul8HIuHJZuMyxJJ7ZHajj3gBM6KAs4mnnE6f7GiJIPC"
```
All further examples assume you have token set in the env.

## Usage
Create a map with a single layer and upload your files.
```bash
felt-upload map data.geojson
```
You can also specify a bunch of optional parameters.
```bash
felt-upload map --title "My new map" --layer-name "Great data" data.geojson
```
Keep in mind, `felt-upload` is pretty straighforward and does not know much about different geo file formats, so if you use shapefiles, you need to specify all the files explicitly:
```bash
felt-upload map --title "My new map with shapefiles" shapefile.shx shapefile.shp shapefile.prj shapefile.dbf shapefile.cst
```
Or use a zip archive
```bash
felt-upload map --title "My new map with zipped shapefiles" shapefile_inside.zip
```

## More use cases
### Multiple layers
Create multiple layers on a single map
```bash
felt-upload map --title "Multilayer"
felt-upload layer <map-id> --layer-name "My point data" dataset.geojson
felt-upload layer <map-id> --layer-name "My other data" dataset-2.geojson
felt-upload layer-import <map-id> --layer-name "My layer from url" http://example.com/path-to-data
```

### Existing map
Want to add layer to already existing map?
Grab map `id` from the url as [explained here](), e.g. for https://felt.com/map/Untitled-Map-Cwc6EdieQdyXgyPMgDmYBC?loc=37.807,-122.271,14z you need a part after the map name and before the `?`: `Cwc6EdieQdyXgyPMgDmYBC`.
