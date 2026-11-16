"""Cut the period-map pictures the playbacks show from the full scans. The scans are too large for the repository; put one under maps/
and run this to rebuild that battle's pictures:

  maps/gettysburg/map_full.png   Bachelder 1876, first day    ->  playbacks/gettysburg/map_wide.jpg, map.jpg
  maps/trenton/map_full.png      Wiederhold 1776              ->  playbacks/trenton/sketch.jpg

The crops below must match the corners on the workbook's Maps sheet.
"""
import os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def gettysburg(scan, out):
    # the mapped area of the sheet, in scan pixels, at 0.4 of scan resolution; the ground of the first morning on top at 0.8
    X0, Y0, X1, Y1 = 650, 1178, 7300, 8120; DET = (650, 1380, 5160, 4100); SC, SCW = 0.8, 0.4
    full = Image.open(scan).convert('RGB')
    im = full.crop(DET).resize((round((DET[2] - DET[0]) * SC), round((DET[3] - DET[1]) * SC)), Image.LANCZOS); im.save(out + '/map.jpg', quality=80, optimize=True, progressive=True)
    im = full.crop((X0, Y0, X1, Y1)).resize((round((X1 - X0) * SCW), round((Y1 - Y0) * SCW)), Image.LANCZOS); im.save(out + '/map_wide.jpg', quality=78, optimize=True, progressive=True)


def trenton(scan, out):
    im = Image.open(scan).convert('RGB'); w, h = im.size   # the whole sketch at 0.7 of scan resolution (positions on it are in these pixels)
    im.resize((round(w * 0.7), round(h * 0.7)), Image.LANCZOS).save(out + '/sketch.jpg', quality=82, optimize=True, progressive=True)


if __name__ == '__main__':
    for name, fn in (('gettysburg', gettysburg), ('trenton', trenton)):
        scan = '%s/maps/%s/map_full.png' % (ROOT, name)
        if os.path.exists(scan): fn(scan, '%s/playbacks/%s' % (ROOT, name)); print(name, 'pictures rebuilt')
        else: print(name, 'scan not found: pictures left as they are')
