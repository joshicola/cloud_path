import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

from cloud_path import CloudPath
from fsspec import filesystem
from fsspec.spec import AbstractFileSystem


class TestCloudPath(unittest.TestCase):
    def setUp(self):
        self.mock_filesystem = Mock(spec=AbstractFileSystem)
        self.cloud_path = CloudPath(
            "/path/to/resource", filesystem=self.mock_filesystem
        )

    def test_new_with_filesystem(self):
        self.assertIsInstance(self.cloud_path, CloudPath)
        self.assertEqual(self.cloud_path.filesystem, self.mock_filesystem)

    def test_new_without_filesystem(self):
        local_path = CloudPath("/local/path")
        self.assertIsInstance(local_path, Path)
        self.assertNotIsInstance(local_path, CloudPath)

    def test_get_fs_path(self):
        self.assertEqual(self.cloud_path._get_fs_path(), "/path/to/resource")

    def test_ls(self):
        self.mock_filesystem.ls.return_value = ["file1", "file2"]
        result = list(self.cloud_path.ls())
        self.mock_filesystem.ls.assert_called_once_with("/path/to/resource")
        self.assertEqual(result, ["file1", "file2"])

    def test_glob(self):
        self.mock_filesystem.glob.return_value = ["file1", "file2"]
        result = list(self.cloud_path.glob("*.txt"))
        self.mock_filesystem.glob.assert_called_once_with("/path/to/resource/*.txt")
        self.assertEqual(
            result,
            [
                CloudPath("file1", filesystem=self.mock_filesystem),
                CloudPath("file2", filesystem=self.mock_filesystem),
            ],
        )

    def test_exists(self):
        self.mock_filesystem.exists.return_value = True
        self.assertTrue(self.cloud_path.exists())
        self.mock_filesystem.exists.assert_called_once_with("/path/to/resource")

    def test_is_dir(self):
        self.mock_filesystem.isdir.return_value = True
        self.assertTrue(self.cloud_path.is_dir())
        self.mock_filesystem.isdir.assert_called_once_with("/path/to/resource")

    def test_is_file(self):
        self.mock_filesystem.isfile.return_value = True
        self.assertTrue(self.cloud_path.is_file())
        self.mock_filesystem.isfile.assert_called_once_with("/path/to/resource")

    def test_iterdir(self):
        self.mock_filesystem.ls.return_value = ["file1", "file2"]
        result = list(self.cloud_path.iterdir())
        self.mock_filesystem.ls.assert_called_once_with("/path/to/resource")
        self.assertEqual(
            result,
            [
                CloudPath("file1", filesystem=self.mock_filesystem),
                CloudPath("file2", filesystem=self.mock_filesystem),
            ],
        )

    def test_mkdir(self):
        self.mock_filesystem = filesystem("file")
        with TemporaryDirectory() as tmpdir:
            add_path = Path(tmpdir) / "path"
            self.cloud_path = CloudPath(add_path, filesystem=self.mock_filesystem)
            self.cloud_path.mkdir(exist_ok=False)
            assert self.cloud_path.exists()

            self.cloud_path.mkdir(exist_ok=True)
            assert self.cloud_path.exists()

    def test_rmdir(self):
        self.cloud_path.rmdir()
        self.mock_filesystem.rmdir.assert_called_once_with("/path/to/resource")

    def test_unlink(self):
        self.cloud_path.unlink()
        self.mock_filesystem.delete.assert_called_once_with("/path/to/resource")

    def test_remove(self):
        self.cloud_path.remove()
        self.mock_filesystem.delete.assert_called_once_with("/path/to/resource")

    def test_rm(self):
        self.cloud_path.rm()
        self.mock_filesystem.delete.assert_called_once_with("/path/to/resource")

    def test_open(self):
        mock_open = Mock()
        self.mock_filesystem.open.return_value = mock_open
        result = self.cloud_path.open()
        self.mock_filesystem.open.assert_called_once_with("/path/to/resource", "r")
        self.assertEqual(result, mock_open)

    def test_read_text(self):
        self.mock_filesystem = filesystem("file")
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "file.txt"
            file_path.write_text("file content")
            cloud_path = CloudPath(file_path, filesystem=self.mock_filesystem)
            result = cloud_path.read_text()
            self.assertEqual(result, "file content")

    def test_write_text(self):
        self.mock_filesystem = filesystem("file")
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "file.txt"
            cloud_path = CloudPath(file_path, filesystem=self.mock_filesystem)
            cloud_path.write_text("new content")
            self.assertEqual(file_path.read_text(), "new content")

    def test_read_bytes(self):
        self.mock_filesystem = filesystem("file")
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "file.txt"
            file_path.write_bytes(b"file content")
            self.cloud_path = CloudPath(file_path, filesystem=self.mock_filesystem)
            result = self.cloud_path.read_bytes()
            self.assertEqual(result, b"file content")

    def test_write_bytes(self):
        self.mock_filesystem = filesystem("file")
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "file.txt"
            self.cloud_path = CloudPath(file_path, filesystem=self.mock_filesystem)
            self.cloud_path.write_bytes(b"new content")
            self.assertEqual(file_path.read_bytes(), b"new content")

    def test_rename(self):
        new_path = self.cloud_path.rename("/new/path")
        self.mock_filesystem.mv.assert_called_once_with(
            "/path/to/resource", "/new/path"
        )
        self.assertEqual(
            new_path, CloudPath("/new/path", filesystem=self.mock_filesystem)
        )

    def test_truediv(self):
        self.mock_filesystem = filesystem("file")
        self.cloud_path = CloudPath(
            "/path/to/resource", filesystem=self.mock_filesystem
        )
        new_path = self.cloud_path / "subdir"
        self.assertEqual(
            new_path,
            CloudPath("/path/to/resource/subdir", filesystem=self.mock_filesystem),
        )

    def test_str(self):
        self.assertEqual(str(self.cloud_path), "/path/to/resource")

    def test_repr(self):
        self.assertEqual(repr(self.cloud_path), "CloudPath('/path/to/resource')")


if __name__ == "__main__":
    unittest.main()
