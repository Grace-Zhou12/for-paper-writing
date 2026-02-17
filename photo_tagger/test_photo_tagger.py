"""Tests for photo_tagger core logic."""

import json
import os
import shutil
import tempfile
import unittest

from photo_tagger import (
    ALL_EXTENSIONS,
    is_supported_file,
    load_tag_records,
    save_tag_records,
    tag_and_move_file,
)


class TestIsSupportedFile(unittest.TestCase):
    """Tests for the is_supported_file helper."""

    def test_common_image_formats(self):
        for ext in (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"):
            self.assertTrue(is_supported_file(f"photo{ext}"), ext)

    def test_raw_formats(self):
        for ext in (".cr2", ".cr3", ".nef", ".arw", ".dng"):
            self.assertTrue(is_supported_file(f"raw_photo{ext}"), ext)

    def test_video_formats(self):
        for ext in (".mp4", ".mov", ".avi", ".mkv"):
            self.assertTrue(is_supported_file(f"video{ext}"), ext)

    def test_other_supported_formats(self):
        for ext in (".psd", ".pdf", ".svg"):
            self.assertTrue(is_supported_file(f"file{ext}"), ext)

    def test_unsupported_format(self):
        self.assertFalse(is_supported_file("document.docx"))
        self.assertFalse(is_supported_file("data.csv"))

    def test_case_insensitive(self):
        self.assertTrue(is_supported_file("PHOTO.JPG"))
        self.assertTrue(is_supported_file("Photo.Png"))


class TestTagRecords(unittest.TestCase):
    """Tests for load/save tag records."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.record_path = os.path.join(self.tmpdir, "records.json")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_load_missing_file(self):
        self.assertEqual(load_tag_records(self.record_path), {})

    def test_save_and_load(self):
        data = {"/photos/a.jpg": ["landscape", "sunset"]}
        save_tag_records(data, self.record_path)
        loaded = load_tag_records(self.record_path)
        self.assertEqual(loaded, data)

    def test_unicode_tags(self):
        data = {"/photos/b.jpg": ["风景", "日落"]}
        save_tag_records(data, self.record_path)
        loaded = load_tag_records(self.record_path)
        self.assertEqual(loaded, data)


class TestTagAndMoveFile(unittest.TestCase):
    """Tests for tag_and_move_file."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.src_dir = os.path.join(self.tmpdir, "source")
        self.dest_dir = os.path.join(self.tmpdir, "dest")
        os.makedirs(self.src_dir)
        os.makedirs(self.dest_dir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _create_file(self, name: str, content: str = "data") -> str:
        path = os.path.join(self.src_dir, name)
        with open(path, "w") as fh:
            fh.write(content)
        return path

    # -- basic move ---------------------------------------------------------

    def test_single_tag_move(self):
        src = self._create_file("photo.jpg")
        results = tag_and_move_file(src, ["landscape"], self.dest_dir)

        self.assertIn("landscape", results)
        self.assertTrue(os.path.isfile(results["landscape"]))
        self.assertFalse(os.path.isfile(src))  # original removed

    def test_multiple_tags_move(self):
        src = self._create_file("photo.jpg")
        results = tag_and_move_file(src, ["landscape", "sunset"], self.dest_dir)

        self.assertEqual(len(results), 2)
        # First tag: moved; second tag: copied from new location.
        for dest in results.values():
            self.assertTrue(os.path.isfile(dest))

    # -- copy mode ----------------------------------------------------------

    def test_single_tag_copy(self):
        src = self._create_file("photo.jpg")
        results = tag_and_move_file(src, ["portrait"], self.dest_dir, copy=True)

        self.assertTrue(os.path.isfile(results["portrait"]))
        self.assertTrue(os.path.isfile(src))  # original kept

    # -- collision handling -------------------------------------------------

    def test_name_collision(self):
        src1 = self._create_file("photo.jpg", "v1")
        tag_and_move_file(src1, ["nature"], self.dest_dir, copy=True)

        src2 = self._create_file("photo.jpg", "v2")
        results = tag_and_move_file(src2, ["nature"], self.dest_dir, copy=True)

        # Should have been renamed to photo_1.jpg
        self.assertIn("_1", os.path.basename(results["nature"]))

    # -- tag record ---------------------------------------------------------

    def test_records_created(self):
        src = self._create_file("photo.jpg")
        record_path = os.path.join(self.dest_dir, "records.json")
        tag_and_move_file(
            src, ["city"], self.dest_dir, copy=True, record_path=record_path
        )

        records = load_tag_records(record_path)
        self.assertTrue(len(records) > 0)
        first_key = next(iter(records))
        self.assertIn("city", records[first_key])

    # -- error handling -----------------------------------------------------

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            tag_and_move_file("/no/such/file.jpg", ["tag"], self.dest_dir)

    def test_empty_tags_raises(self):
        src = self._create_file("photo.jpg")
        with self.assertRaises(ValueError):
            tag_and_move_file(src, [], self.dest_dir)

    def test_whitespace_only_tags_raises(self):
        src = self._create_file("photo.jpg")
        with self.assertRaises(ValueError):
            tag_and_move_file(src, ["  ", ""], self.dest_dir)

    # -- folder creation ----------------------------------------------------

    def test_tag_folder_created(self):
        src = self._create_file("photo.jpg")
        tag_and_move_file(src, ["wedding"], self.dest_dir)
        self.assertTrue(os.path.isdir(os.path.join(self.dest_dir, "wedding")))


if __name__ == "__main__":
    unittest.main()
