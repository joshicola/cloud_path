# Cloud Path

CloudPath is wrapper around `fsspec.AbstractFileSystem` that provides a RealPath
interface to cloud storage. It is designed to be used with the `pathlib` module, and
provides a `Path` class that can be used to interact with cloud storage in a similar way
to how you would interact with the local file system.
