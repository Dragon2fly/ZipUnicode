__author__ = "Duc Tin"

from pathlib import Path

import pytest

from zip_unicode import ZipHandler

root_folder = ZipHandler('20200524_ドラゴンフライト.zip')
root_folder2 = ZipHandler('20200524_ドラゴンボール.zip')
flat = ZipHandler('20200524_フラット.zip')
flat_pwd = ZipHandler('20200524_フラットpwd.zip')
mixed = ZipHandler('ミックス.zip')
nested_subfolder = ZipHandler('202301-03_hokkaido_jukyu.zip')    # with folder entry registered as a file


def clean_up(path: Path):
    if path.is_dir():
        for f in path.iterdir():
            clean_up(f) if f.is_dir() else f.unlink()
        else:
            path.rmdir()
    else:
        path.unlink()


def test_byte_name():
    res = {b'V\xc3\xb9ng Tr\xe1\xbb\x9di B\xc3\xacnh Y\xc3\xaan.txt': True,
           b'\x84q\x84\x80\x84\x82\x84u\x84y\x84\x83\x84{\x84p\x84\x91.txt': False,
           b'\x83e\x83X\x83g\x83\x8c\x83|\x81[\x83g\x81Q\x83\x8a\x83i\x83b\x83N\x83X\x83m\x81[\x83h.txt': False,
           b'\x91\xbe\x97z\x83o\x83b\x83e\x83\x8a\x81[ver5.txt': False,
           b'\x8co\x89c\x95\xf1\x8d\x90_\x8d\xf7\x82\xbf\x82\xe1\x82\xf1.txt': False,
           }

    for file_info in mixed.zip_ref.infolist():
        is_utf8, name = mixed.byte_name(file_info)
        assert res[name] == is_utf8


def test_guess_encoding():
    assert flat.original_encoding == 'SHIFT_JIS'


def test_get_filename_map():
    names = ['Vùng Trời Bình Yên.txt', 'бореиская.txt', 'テストレポート＿リナックスノード.txt',
             '太陽バッテリーver5.txt', '経営報告_桜ちゃん.txt']
    encodings = ['utf8', 'cp932', 'cp932', 'cp932', 'cp932']

    wrong_encoded = [x.encode(enc) for x, enc in zip(names[1:], encodings[1:])]
    wrong_decoded = [x.decode('cp437') for x in wrong_encoded]
    wrong_decoded.insert(0, 'Vùng Trời Bình Yên.txt')   # utf8 is left intact

    assert mixed.name_map == dict(zip(wrong_decoded, names))


def test_duplicated_root_name():
    assert root_folder._duplicated_root_name()
    assert not root_folder2._duplicated_root_name()
    assert not flat._duplicated_root_name()
    assert not flat_pwd._duplicated_root_name()
    assert not mixed._duplicated_root_name()


def test_is_encrypted():
    assert flat_pwd.is_encrypted()
    assert not flat.is_encrypted()
    assert not mixed.is_encrypted()


def test_extract_individual():
    name = "テストレポート＿リナックスノード.txt".encode('cp932').decode('cp437')
    out = Path('test_extract_individual.txt')
    flat._extract_individual(name, out)
    assert out.read_text(encoding='cp932') == '何もない'
    out.unlink()


def test_extract_all():
    # all filenames have the same encoding
    expect = {'テストレポート＿リナックスノード.txt', '経営報告_桜ちゃん.txt', '太陽バッテリーver5.txt'}
    out = Path('test_extract_all_one_enc')
    flat.extract_all(out)
    assert set(x.name for x in out.iterdir()) == expect
    clean_up(out)

    # some files are UTF8 encoded, some are not
    expect = {'Vùng Trời Bình Yên.txt', 'бореиская.txt', 'テストレポート＿リナックスノード.txt',
              '太陽バッテリーver5.txt', '経営報告_桜ちゃん.txt'}
    out = Path('test_extract_all_mixed_enc')
    mixed.extract_all(out)
    assert set(x.name for x in out.iterdir()) == expect
    clean_up(out)

    # multiple sub-folder with subfolders entry as a file
    # aka malformed zipfile
    expect = {'202301', '202302', '202303'}
    out = Path('test_extract_all_multiple_sub_folder')
    nested_subfolder.extract_all(out)
    assert set(x.name for x in out.iterdir()) == expect
    clean_up(out)


def test_extract_all_with_pwd(caplog):
    expect = {'テストレポート＿リナックスノード.txt', '経営報告_桜ちゃん.txt', '太陽バッテリーver5.txt'}
    out = Path('test_extract_all')

    with pytest.raises(OSError) as e:
        # password input required
        flat_pwd.extract_all(out)

    flat_pwd.password = b'WrongPassword'
    flat_pwd.extract_all(out)

    capture = caplog.text
    assert 'Wrong password!' in capture

    flat_pwd.password = b'password'
    flat_pwd.extract_all(out)
    assert set(x.name for x in out.iterdir()) == expect

    file_1 = Path('test_extract_all/テストレポート＿リナックスノード.txt')
    assert file_1.read_text(encoding='cp932') == '何もない'

    # clean up
    flat_pwd.password = None
    clean_up(out)


def test_extract_all_with_root_folder():
    out1 = Path(root_folder.zip_ref.filename.replace('.zip', ''))
    root_folder.extract_all()
    assert not any(x.is_dir() for x in out1.iterdir())
    clean_up(out1)

    out2 = Path('specified_path')
    root_folder.extract_all(out2)
    assert (out2 / out1.name).exists()
    clean_up(out2)

    out3 = Path('ミックス')
    mixed.extract_all()
    assert out3.exists() and len(list(out3.iterdir())) == 5
    clean_up(out3)


@pytest.mark.parametrize('my_zip', [root_folder, flat, mixed])
def test_fix_it(my_zip):
    my_zip.fix_it()

    name = my_zip.zip_path.stem
    fixed = my_zip.zip_path.parent / (name + '_fixed.zip')
    fixed_zip = ZipHandler(fixed)
    assert fixed_zip.all_utf8

    fixed_zip.zip_ref.close()
    clean_up(fixed)
