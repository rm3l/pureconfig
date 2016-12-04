# Structure

Every spec is separated into two files:

1. `main.pure` This is the input to the parser.
1. `main.json` This is the exhaustive list of configurations that should be present in the final output.

## Directories

Specs are loosly grouped as `major_feature/case/file.
Most cases will have a single main.{pure,json} pair.
The structure exists to support hermetic testing on including additional files.

The `unstable` directory is used for features that are currently in development and are subject to change.
Implementations consistent with the version of this repository don't have to implement these features, but they may.
Any use of these features in subject to breaking with newer iterations of the feature's development.
