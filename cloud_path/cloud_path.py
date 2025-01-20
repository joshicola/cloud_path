from pathlib import Path
from typing import Optional, Union

from fsspec.spec import AbstractFileSystem


class CloudPath(Path):
    def __new__(
        cls,
        *args: Union[str, Path, "CloudPath", AbstractFileSystem],
        filesystem: AbstractFileSystem = None,
    ):
        """Constructor for the CloudPath class.

        Args:
            *args (Union[str, Path, "CloudPath", AbstractFileSystem]): Objects that can be joined to form a path.
            filesystem (AbstractFileSystem, optional): The filesystem to use. Defaults to None.

        Returns:
            CloudPath: An initialized CloudPath object.
        """
        if filesystem is None and isinstance(args[-1], AbstractFileSystem):
            path = Path(*args[:-1])
            filesystem = args[-1]
        else:
            # Join multiple path components
            path = Path(*args)

        # If any component is a CloudPath, inherit its filesystem
        if any(isinstance(arg, CloudPath) for arg in args):
            cloud_arg = next(arg for arg in args if isinstance(arg, CloudPath))
            filesystem = cloud_arg.filesystem

        # If we do not have an explicit filesystem, return a regular Path object
        if not filesystem:
            return super().__new__(Path, str(path))

        # Create the CloudPath instance
        obj = super().__new__(cls, str(path))
        obj.filesystem = filesystem

        return obj

    def _get_fs_path(self) -> str:
        """Return the path as a string.

        Returns:
            str: The path as a string.
        """
        return super().__str__()  # str(super(CloudPath, self))

    def ls(self):
        """Get the files and directories in the path.

        # TODO: Extend to support more arguments consistent with other filesystems.

        Returns:
            list: list of strings representing the files and directories in the path.
        """
        return self.filesystem.ls(self._get_fs_path())

    def glob(self, pattern: str, *, recursive: bool = False):
        for item in self.filesystem.glob(self._get_fs_path() + "/" + pattern):
            yield CloudPath(item, filesystem=self.filesystem)

    def exists(self, *args, **kwargs) -> bool:
        return self.filesystem.exists(self._get_fs_path())

    def is_dir(self) -> bool:
        return self.filesystem.isdir(self._get_fs_path())

    def is_file(self) -> bool:
        return self.filesystem.isfile(self._get_fs_path())

    def iterdir(self):
        for item in self.filesystem.ls(self._get_fs_path()):
            yield CloudPath(item, filesystem=self.filesystem)

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        if not exist_ok and self.exists():
            raise FileExistsError(f"Directory '{self}' already exists")
        self.filesystem.makedirs(self._get_fs_path(), exist_ok=exist_ok)

    def rmdir(self):
        self.filesystem.rmdir(self._get_fs_path())

    def unlink(self, missing_ok=False):
        try:
            self.filesystem.delete(self._get_fs_path())
        except FileNotFoundError:
            if not missing_ok:
                raise

    def remove(self, missing_ok=False):
        self.unlink(missing_ok)

    def rm(self, missing_ok=False):
        self.unlink(missing_ok)

    def open(self, mode="r", *args, **kwargs):
        return self.filesystem.open(self._get_fs_path(), mode, *args, **kwargs)

    def read_text(
        self, encoding: Optional[str] = None, errors: Optional[str] = None
    ) -> str:
        with self.open("r") as f:
            return f.read()

    def write_text(
        self,
        data: str,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
    ):
        with self.open("w") as f:
            f.write(data)

    def read_bytes(self) -> bytes:
        with self.open("rb") as f:
            return f.read()

    def write_bytes(self, data: bytes):
        with self.open("wb") as f:
            f.write(data)

    def rename(self, target: Union[str, Path]) -> "CloudPath":
        self.filesystem.mv(self._get_fs_path(), str(target))
        return CloudPath(str(target), filesystem=self.filesystem)

    def __truediv__(self, other: str) -> "CloudPath":
        return CloudPath(self._get_fs_path(), other, filesystem=self.filesystem)

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return f"CloudPath('{self._get_fs_path()}')"


# Example usage:
# from fsspec import AbstractFileSystem
# fs = SomeConcreteFileSystem()  # Replace with actual fsspec filesystem, e.g., S3, GCS
# cloud_path = CloudPath('/path/to/resource', fs)
