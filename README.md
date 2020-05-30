# ZipUnicode
Make extracted unreadable filename problem gone away. 

## Install:
Using pip: `pip install ZipUnicode`

Beside installing `zip_unicode` package, 
this will also create an executable file `zipu` in the syspath 
for you to work with `zip` file directly from the console. 

## Filename encoding inside a zip file
Everyone agrees what a zip file is and how to make one. 
That is the way to turn a collection of files into a sequence of bytes 
and put a `.zip` at the end of the name of a newly created file. 
But no one said anything about how filename should be handled. 
So it is up to the zip extracting program to interpret that sequence of bytes into filename.  

Most OS use UTF-8 for filename encoding and flip a bit in the zip file to indicate that.
However, Windows is not a case. For different languages, Windows uses different `code page`s
to encode filename. So, if you create a zip file containing a file named `ê.txt` on Linux and 
extract it on Windows, you may got something like `├¬.txt` or `ﾃｪ.txt`. 

The exact filename depends on the `code page` or `language` that Windows is using. 
The same thing also happens when a zip file was created on Windows,
contains non-ascii filename, and then extracted on Linux or on Windows that use different `code page`s.

All that means if the filename wasn't encoded by `UTF-8` `encoding (or code page)`,
then there is no easy way to knows which `encoding` that was used when extracting the file. 

## Overview
You will use `zipu` to interact with zip file.

```bash
$ zipu -h
```

```bash
usage: zipu [-h] [--extract] [--fix] [--encoding ENCODING]
            [--password PASSWORD]
            zipfile [destination]

Fix filename encoding error inside a zip file.

positional arguments:
  zipfile               path to zip file
  destination           folder path to extract zip file

optional arguments:
  -h, --help            show this help message and exit
  --extract, -x         extract the zipfile to specified destination
  --fix, -f             create a new zip file with UTF-8 file names
  --encoding ENCODING, -enc ENCODING
                        zip file used encoding: shift-jis, cp932...
  --password PASSWORD, -pwd PASSWORD
                        password to extract zip file
```

Extracting a zip file is as simple as `zipu -x file.zip`. 
Files are extracted into the folder that has the same name as `file.zip` without `.zip`
and stays on the same folder path as `file.zip`. Filename `encoding` is handled automatically.

You can also ensure your zip file being opened correctly on all computers by `zipu -f file.zip`.
This will create a new `file_fixed.zip` contains all file names encoded with `UTF-8`.

## Usage:
1. View content of the zip file:
   
   You simply point `zipu` to your zip file's path as follow:
   
    ```bash
    zipu path/to/file.zip
    ```
   
   This makes `zipu` do the following:
    * automatically guess the encoding that was used to encode file names
    * check if the file was password encrypted 
    * give you a default extract destination if you don't provide any
    
   Then, it will show a summarization of the contents of that zip file, 
   something similar to the following:
   
       D:\tmp>zipu 20200524_ドラゴンフライト.zip
   
   ```bash
     * Detected encoding  :  SHIFT_JIS | Language:Japanese | Confidence:99%
     * Default destination:  D:\tmp
     * Password protected :  False
    --------------------------- try encoding: SHIFT_JIS ---------------------------
    20200524_ドラゴンフライト/
    20200524_ドラゴンフライト/テストレポート＿リナックスノード.txt
    20200524_ドラゴンフライト/太陽バッテリーver5.txt
    20200524_ドラゴンフライト/経営報告_桜ちゃん.txt
    -------------------------------------------------------------------------------
    Add '-enc ENCODING' to see filename shown in encoding ENCODING (mbcs, cp932, shift-jis,...)
    Add '-x' flag to extract all files to default destination
   ```
   
   If there is a root folder inside and it has the same name as the zip file as above example, 
   `default destination` will be the parent folder of the zip file.
   Otherwise, `default destination` will point to a subdirectory 
   that has the name of the zip file as the following case:
   
       D:\tmp>zipu 20200524_ドラゴンボール.zip
   
   ```bash
     * Detected encoding  :  SHIFT_JIS | Language:Japanese | Confidence:99%
     * Default destination:  D:\tmp\20200524_ドラゴンボール
     * Password protected :  False
    --------------------------- try encoding: SHIFT_JIS ---------------------------
    テストレポート＿リナックスノード.txt
    太陽バッテリーver5.txt
    経営報告_桜ちゃん.txt
    -------------------------------------------------------------------------------
    Add '-enc ENCODING' to see filename shown in encoding ENCODING (mbcs, cp932, shift-jis,...)
    Add '-x' flag to extract all files to default destination
   ```

2. View content with a specific encoding:

   Encoding auto-detection is not always correct. When the sample is too little
   and some parts of `A` encoding are in `B` encoding, `B` may be wrongly detected
   instead of `A`. In such cases, you can specify the encoding which you believe
   is the correct one with `-enc ENCODING` switch.
   
       D:\tmp>zipu 20200524_ドラゴンボール.zip -enc cp932
   
   ```bash
     * Default destination:  D:\tmp\20200524_ドラゴンボール
     * Password protected :  False
    --------------------------- try encoding: cp932 ---------------------------
    テストレポート＿リナックスノード.txt
    太陽バッテリーver5.txt
    経営報告_桜ちゃん.txt
    ---------------------------------------------------------------------------
    Add '-enc ENCODING' to see filename shown in encoding ENCODING (mbcs, cp932, shift-jis,...)
    Add '-x' flag to extract all files to default destination
   ```
   
   In case that your specified `ENCODING` is wrong and cannot decode some bytes,
   these unknown bytes will be replaced by a lot of `�`.
   
       D:\tmp>zipu 20200524_ドラゴンボール.zip -enc ascii
   
   ```bash
     * Default destination:  D:\tmp\20200524_ドラゴンボール
     * Password protected :  False
    --------------------------- try encoding: ascii ---------------------------
    �e�X�g���|�[�g�Q���i�b�N�X�m�[�h.txt
    ���z�o�b�e���[ver5.txt
    �o�c��_�������.txt
    ---------------------------------------------------------------------------
    Add '-enc ENCODING' to see filename shown in encoding ENCODING (mbcs, cp932, shift-jis,...)
    Add '-x' flag to extract all files to default destination
   ```
   
   Or those bytes are mapped into completely different characters:
   
       D:\tmp>zipu 20200524_ドラゴンボール.zip -enc utf16
   
   ```bash
     * Default destination:  D:\tmp\20200524_ドラゴンボール
     * Password protected :  False
    --------------------------- try encoding: utf16 ---------------------------
    斃境枃貃粃宁枃冁誃榃抃亃境涃宁梃琮瑸
    뺑窗澃抃斃誃宁敶㕲琮瑸
    澌掉邍赟苷芿苡⻱硴�
    ---------------------------------------------------------------------------
    Add '-enc ENCODING' to see filename shown in encoding ENCODING (mbcs, cp932, shift-jis,...)
    Add '-x' flag to extract all files to default destination
   ```
   
   Only when auto-detection failed, it is your responsibility to decide which `ENCODING` is the correct one.
   
   **Warning**: If your console uses non-full `UTF-8` font as in the case of Windows,
   some `UTF-8` characters are shown as a dot `・`. 
   This is not a result of wrong encoding but rather unsupported characters by the font.
   
3. Extract the zip file:

    Usually, encoding auto-detection works just fine so you can jump right to extraction with <br>
    `zipu -x path/to/file.zip`. The `-x` argument can be either placed **before or after** the path to the zip file.
    
        D:\tmp>zipu 20200524_ドラゴンフライト.zip -x
    
    ```bash
     * Detected encoding  :  SHIFT_JIS | Language:Japanese | Confidence:99%
    Extracting: 20200524_ドラゴンフライト/テストレポート＿リナックスノード.txt
    Extracting: 20200524_ドラゴンフライト/太陽バッテリーver5.txt
    Extracting: 20200524_ドラゴンフライト/経営報告_桜ちゃん.txt
    Finished
   ``` 
   
   As mentioned before, without specifying the `destination`, zip file is extracted to
   the directory in the same path and has the name of that zip file.<br> 
   In the above example, that would be `D:\tmp\20200524_ドラゴンフライト`.
   
   When extract `destination` is specified, you add it right after the zip file's path as:
   
       zipu -x path/to/file.zip path/to/extract 
   
   If the output file names are unreadable, 
   you have to guess the `ENCODING` with `-enc` switch as described in **2. View content with a specified encoding**.
   Then you can use that `ENCODING` to extract zip file:
   
       zipu path/to/file.zip -x -enc ENCODING
   
4. A Password protected zip file:

    If a zip file is encrypted, ` * Password protected :  True` will show up when viewing its content. 
    When extracting the zip file, you will be asked for `password` if you haven't provided any.
    You can also specify password directly in the command as follows:
    
        zipu path/to/file.zip -x -pwd PASSWORD  

5. Mixed contents:

   Some zip files are very tricky. It contains file names of different encodings. Some `UTF-8`, some not.
   For `UTF-8` marked files, `zipu` will leave it as is while trying different `ENCODING` on other files.
   `UTF-8` encoded filename has `(UTF-8) ` string prefixed in the content view:
   
       D:\tmp>zipu ミックス.zip
   
   ```bash
    * Detected encoding  :  SHIFT_JIS | Language:Japanese | Confidence:63%
    * Default destination:  D:\tmp\ミックス
    * Password protected :  False
   --------------------------- try encoding: SHIFT_JIS ---------------------------
   (UTF-8) Vùng Trời Bình Yên.txt
   бореиская.txt
   テストレポート＿リナックスノード.txt
   太陽バッテリーver5.txt
   経営報告_桜ちゃん.txt
   -------------------------------------------------------------------------------
   Add '-enc ENCODING' to see filename shown in encoding ENCODING (mbcs, cp932, shift-jis,...)
   Add '-x' flag to extract all files to default destination
   ```
   
   When extracting, `UTF-8` encoded filename will not wrongly be decoded with detected `ENCODING` 
   so that you can read it as is. 
   
   **Warning**: `zipu` cannot handle zip file that contains three or more encodings, or two encodings
   but neither is `UTF-8`. In such cases, you have to extract the zip file for each encoding.

6. Fixing a zip file:

   If you make a zip file contains file names which are not in `UTF-8` nor `ASCII` encoding, 
   then you can ensure that your colleagues who use computers of different language can 
   open the zip just fine as follows:
   
   ```bash
   zipu -f path/to/file.zip
   ```
   
   This first extracts your zip file (and convert all file names to `UTF-8`). 
   Then it compresses extracted contents and adds `_fixed` suffix to the zip filename.
   The fixed zip file is on the same path as the original one.