from __future__ import print_function, division, absolute_import, unicode_literals
from fontTools.misc.py23 import *
from fontTools.misc.testTools import parseXML
from fontTools.misc.textTools import deHexStr
from fontTools.misc.xmlWriter import XMLWriter
from fontTools.ttLib import TTLibError
from fontTools.ttLib.tables._m_e_t_a import table__m_e_t_a
import unittest


# From a real font on MacOS X, but substituted 'bild' tag by 'TEST',
# and shortened the payload. Note that from the 'meta' spec, one would
# expect that header.dataOffset is 0x0000001C (pointing to the beginning
# of the data section) and that dataMap[0].dataOffset should be 0 (relative
# to the beginning of the data section). However, in the fonts that Apple
# ships on  MacOS X 10.10.4, dataMap[0].dataOffset is actually relative
# to the beginning of the 'meta' table, i.e. 0x0000001C again. While the
# following test data is invalid according to the 'meta' specification,
# it is reflecting the 'meta' table structure in all Apple-supplied fonts.
META_DATA = deHexStr(
    "00 00 00 01 00 00 00 00 00 00 00 1C 00 00 00 01 "
    "54 45 53 54 00 00 00 1C 00 00 00 04 CA FE BE EF")

# The 'dlng' and 'slng' tag with text data containing "augmented" BCP 47
# comma-separated or comma-space-separated tags. These should be UTF-8 encoded
# text.
META_DATA_TEXT = deHexStr(
    "00 00 00 01 00 00 00 00 00 00 00 28 00 00 00 02 "
    "64 6C 6E 67 00 00 00 28 00 00 00 0E 73 6C 6E 67 "
    "00 00 00 36 00 00 00 0E 4C 61 74 6E 2C 47 72 65 "
    "6B 2C 43 79 72 6C 4C 61 74 6E 2C 47 72 65 6B 2C "
    "43 79 72 6C")

class MetaTableTest(unittest.TestCase):
    def test_decompile(self):
        table = table__m_e_t_a()
        table.decompile(META_DATA, ttFont={"meta": table})
        self.assertEqual({"TEST": b"\xCA\xFE\xBE\xEF"}, table.data)

    def test_compile(self):
        table = table__m_e_t_a()
        table.data["TEST"] = b"\xCA\xFE\xBE\xEF"
        self.assertEqual(META_DATA, table.compile(ttFont={"meta": table}))

    def test_decompile_text(self):
        table = table__m_e_t_a()
        table.decompile(META_DATA_TEXT, ttFont={"meta": table})
        self.assertEqual({"dlng": u"Latn,Grek,Cyrl",
                          "slng": u"Latn,Grek,Cyrl"}, table.data)

    def test_compile_text(self):
        table = table__m_e_t_a()
        table.data["dlng"] = u"Latn,Grek,Cyrl"
        table.data["slng"] = u"Latn,Grek,Cyrl"
        self.assertEqual(META_DATA_TEXT, table.compile(ttFont={"meta": table}))

    def test_toXML(self):
        table = table__m_e_t_a()
        table.data["TEST"] = b"\xCA\xFE\xBE\xEF"
        writer = XMLWriter(BytesIO())
        table.toXML(writer, {"meta": table})
        xml = writer.file.getvalue().decode("utf-8")
        self.assertEqual([
            '<hexdata tag="TEST">',
                'cafebeef',
            '</hexdata>'
        ], [line.strip() for line in xml.splitlines()][1:])

    def test_fromXML(self):
        table = table__m_e_t_a()
        for name, attrs, content in parseXML(
                '<hexdata tag="TEST">'
                '    cafebeef'
                '</hexdata>'):
            table.fromXML(name, attrs, content, ttFont=None)
        self.assertEqual({"TEST": b"\xCA\xFE\xBE\xEF"}, table.data)

    def test_toXML_text(self):
        table = table__m_e_t_a()
        table.data["dlng"] = u"Latn,Grek,Cyrl"
        writer = XMLWriter(BytesIO())
        table.toXML(writer, {"meta": table})
        xml = writer.file.getvalue().decode("utf-8")
        self.assertEqual([
            '<text tag="dlng">',
            'Latn,Grek,Cyrl',
            '</text>'
        ], [line.strip() for line in xml.splitlines()][1:])

    def test_fromXML_text(self):
        table = table__m_e_t_a()
        for name, attrs, content in parseXML(
                '<text tag="dlng">'
                '    Latn,Grek,Cyrl'
                '</text>'):
            table.fromXML(name, attrs, content, ttFont=None)
        self.assertEqual({"dlng": u"Latn,Grek,Cyrl"}, table.data)


if __name__ == "__main__":
    unittest.main()