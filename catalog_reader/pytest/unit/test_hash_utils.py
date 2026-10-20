import os

from catalog_reader.hash_utils import get_hash_of_directory


def create_lib(path):
    path.mkdir(parents=True)
    (path / 'render.py').write_text('render')
    return path


def test_hash_matches_stored_format(tmp_path):
    # Values from the `find | sha256sum | sort | awk | sha256sum` pipeline the catalog hashes were made with
    empty = tmp_path / 'empty'
    empty.mkdir()
    assert get_hash_of_directory(str(empty)) == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    lib = create_lib(tmp_path / 'lib')
    assert get_hash_of_directory(str(lib)) == '35b769b3e1a0175a56c0aa31ad1956e934ff97da715bf7bb1133375b6b7dbd6b'


def test_hash_skips_symlinks_and_special_files(tmp_path):
    lib = create_lib(tmp_path / 'lib')
    expected = get_hash_of_directory(str(lib))
    (lib / 'link_to_file').symlink_to(lib / 'render.py')
    (lib / 'link_to_dir').symlink_to(lib)
    (lib / 'broken_link').symlink_to(lib / 'missing')
    os.mkfifo(lib / 'fifo')
    assert get_hash_of_directory(str(lib)) == expected


def test_hash_ignores_tests_and_pycache(tmp_path):
    lib = create_lib(tmp_path / 'lib')
    expected = get_hash_of_directory(str(lib))
    (lib / 'tests').mkdir()
    (lib / 'tests/test_render.py').write_text('test')
    (lib / '__pycache__').mkdir()
    (lib / '__pycache__/render.cpython-313.pyc').write_text('bytecode')
    assert get_hash_of_directory(str(lib)) == expected


def test_hash_changes_with_content(tmp_path):
    lib = create_lib(tmp_path / 'lib')
    expected = get_hash_of_directory(str(lib))
    (lib / 'render.py').write_text('changed')
    assert get_hash_of_directory(str(lib)) != expected


def test_hash_of_excluded_named_root(tmp_path):
    # Only entries inside the directory are excluded, never the directory itself
    lib = create_lib(tmp_path / 'tests')
    empty = tmp_path / 'empty'
    empty.mkdir()
    assert get_hash_of_directory(str(lib)) != get_hash_of_directory(str(empty))
