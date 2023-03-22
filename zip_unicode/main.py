__author__ = "Duc Tin"
__version__ = "1.0.0"

import getpass
import logging
import shutil
import sys
import zipfile
import tempfile
from pathlib import Path
from argparse import ArgumentParser

import chardet


# Disable chardet logger
logging.getLogger('chardet').level = logging.ERROR

# Config our logger
logging.basicConfig(format='%(message)s', stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('zip_unicode')


def zip_it(base_name, root_dir):
    logger.info("Creating archive:")
    shutil.make_archive(base_name, 'zip', root_dir, logger=logger)


class ZipHandler:
    def __init__(self, path: str, encoding: str = None,
                 password: bytes = None, extract_path: str = ""):

        self.zip_path = Path(path)
        self.zip_ref = zipfile.ZipFile(self.zip_path)

        self.all_utf8 = None
        self.original_encoding = encoding or self.guess_encoding()
        self.password = password
        self.name_map = self._get_filename_map()

        if self._duplicated_root_name():
            self.default_destination = self.zip_path.parent.absolute()
        else:
            self.default_destination = self.zip_path.parent.absolute() / self.zip_path.stem
        self.destination = Path(extract_path) if extract_path else self.default_destination

    @staticmethod
    def byte_name(file_info: zipfile.ZipInfo) -> (bool, bytes):
        """return path of a zip element in bytes,
            and a flag is True if it is UTF-8 encoded
        """
        is_utf8 = file_info.flag_bits & 0x800
        if not is_utf8:
            # filename is not encoded with utf-8
            return False, file_info.orig_filename.encode("cp437")
        else:
            return True, file_info.orig_filename.encode("utf-8")

    def guess_encoding(self):
        namelist = []

        self.all_utf8 = True
        for file_info in self.zip_ref.infolist():
            utf8, byte_name = self.byte_name(file_info)
            if not utf8:
                namelist.append(byte_name)
                self.all_utf8 = False

        if not self.all_utf8:
            enc = chardet.detect(b' '.join(namelist))
            logger.info(f' * Detected encoding  :  {enc["encoding"]} | '
                        f'Language:{enc["language"]} | '
                        f'Confidence:{enc["confidence"]:.0%} ')
            return enc["encoding"]
        else:
            logger.info(' * All file names are properly in UTF8 encoding')
            return 'UTF_8'

    def _get_filename_map(self) -> dict:
        """ Map unreadable filename to correctly decoded one """
        encoding = self.original_encoding
        name_map = {}
        for file_info in self.zip_ref.infolist():
            if not (file_info.flag_bits & 0x800):
                # filename is not encoded with utf-8
                name_as_bytes:bytes = file_info.orig_filename.encode("cp437")
                name_as_str = name_as_bytes.decode(encoding, errors='replace')
            else:
                name_as_str = file_info.filename

            name_map[file_info.filename] = name_as_str

        return name_map

    def _duplicated_root_name(self) -> bool:
        """Inside zip file is one folder whose name is zip filename"""
        paths = sorted(self.name_map.values())  # make sure the shorted name listed first
        root = paths[0]
        has_root = all(x.startswith(root) for x in paths)
        if not has_root:
            return False

        zipname = self.zip_ref.filename.replace('.zip', '/')
        if zipname.endswith(root):
            return True

    def is_encrypted(self) -> bool:
        """Check if zipfile is password protected"""
        encrypted = False
        for file_info in self.zip_ref.infolist():
            encrypted = bool(file_info.flag_bits & 0x1)
            if encrypted:
                break
        return encrypted

    def fix_it(self):
        """convert filename from nonUTF-8 to UTF-8"""
        with tempfile.TemporaryDirectory() as tmp_folder:
            tmp_folder = Path(tmp_folder)
            self.extract_all(tmp_folder)
            new_name = self.zip_path.parent / (self.zip_path.stem + '_fixed')
            folder_to_zip = tmp_folder      # /self.zip_path.stem
            zip_it(new_name, folder_to_zip)

        if self.is_encrypted():
            logger.warning(f" !!! Fixed zipfile is NOT password protected!")

    def _extract_individual(self, filename: str, output_path: Path,
                            password: bytes = None) -> bool:
        """Extract 'filename' in zipfile to path 'output_path' with password 'password' """

        try:
            with output_path.open("wb+") as output_file:
                stream = self.zip_ref.open(filename, pwd=password)
                shutil.copyfileobj(fsrc=stream, fdst=output_file)
                return True
        except RuntimeError as e:
            if 'Bad password' in str(e):
                logger.error(f"RuntimeError: Wrong password!")
            else:
                logger.error(e)
            return False
        except Exception as e:
            logger.error(e)
            return False

    def extract_all(self, destination: Path = None):
        """Extract content of zipfile with readable filename"""
        password = self.password
        destination = destination or self.destination

        if self.is_encrypted() and not password:
            password = getpass.getpass().encode()

        for original_name, decoded_name in self.name_map.items():
            if decoded_name.endswith("/"):
                # skip subdirectory
                continue

            logger.info(f"Extracting: {decoded_name}")
            fo = destination / decoded_name
            if fo.exists() and fo.is_dir():
                # skip already exists directory
                continue
            parent = fo.parent
            if parent.exists() and parent.is_file():
                # parent should be a directory
                parent.unlink()
            parent.mkdir(parents=True, exist_ok=True)
            extract_ok = self._extract_individual(original_name, fo, password)
            if not extract_ok:
                break
        else:
            logger.info("Finished")

    def __repr__(self):
        basic = f" * Default destination:  {self.default_destination}\n" \
                f" * Password protected :  {self.is_encrypted()}"

        try_enc = (not self.all_utf8) and f' try encoding: {self.original_encoding} ' or ''
        txt = [basic, try_enc.center(79, '-')]
        for file_info in self.zip_ref.infolist():
            if not (file_info.flag_bits & 0x800):
                name_as_bytes = file_info.orig_filename.encode("cp437")
                name_as_str = name_as_bytes.decode(self.original_encoding, "replace")
            else:
                name_as_str = "(UTF-8) " + file_info.filename
            txt.append(name_as_str)
        txt.append('-' * len(txt[1]))

        txt.append("Add '-enc ENCODING' to see filename shown in encoding "
                   "ENCODING (mbcs, cp932, shift-jis,...)")
        txt.append("Add '-x' flag to extract all files to "
                   "default destination")
        return '\n'.join(txt)


def entry_point():
    parser = ArgumentParser(description='Fix filename encoding error '
                                        'inside a zip file.')
    parser.add_argument('zipfile', help='path to zip file')
    parser.add_argument('destination', nargs='?', default="",
                        help='folder path to extract zip file')
    parser.add_argument('--extract', '-x', action='store_true',
                        help='extract the zipfile to specified destination')
    parser.add_argument('--fix', '-f', action='store_true',
                        help='create a new zip file with UTF-8 file names')
    parser.add_argument('--encoding', '-enc',
                        help='zip file used encoding: shift-jis, cp932...')
    parser.add_argument('--password', '-pwd', default='',
                        help='password to extract zip file')

    args = parser.parse_args()
    try:
        if args.extract:
            zhdl = ZipHandler(path=args.zipfile, encoding=args.encoding,
                              password=args.password.encode('utf8'),
                              extract_path=args.destination)
            zhdl.extract_all()
        elif args.fix:
            zhdl = ZipHandler(path=args.zipfile, encoding=args.encoding,
                              password=args.password.encode('utf8'),
                              extract_path=args.dst)
            zhdl.fix_it()
        else:
            zhdl = ZipHandler(path=args.zipfile, encoding=args.encoding)
            print(zhdl)
    # except Exception as e:
    #     logger.error(e)
    finally:
        pass


if __name__ == '__main__':
    entry_point()