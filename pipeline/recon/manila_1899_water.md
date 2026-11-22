# How the water was taken from the engineer map

`manila_1899_picks.json` holds every pixel pick behind `data/recon/manila-1899.geojson`. Most were read by eye from gridded crops.
Three were made by program (method `AI-extracted`), from the 3,840 x 2,847 copy of the Haan map (National Archives 109182890):

1. **The water tint.** The map's water is a pale blue wash. Blue minus red, blurred (2 px), with the paper's own drift taken out by a
   wide median, gives a "blueness" image; water is where it exceeds a threshold (3.0 for the Pasig, 4.5 for the moat, 5.0 for the lagoons).
2. **The Pasig** (`pasig`). Inside a 100-px corridor along today's river (placed by the fit), the pixels that are blue and not inked,
   connected to the river's line, closed (7 px), opened (7 px) and smoothed; holes smaller than 500 px (lettering) filled, larger ones
   (the island below Malacanang) kept. Then by hand: four gaps under lettering and bridges closed (the yellow unit lettering along the
   San Miguel bank hides the bank line), three leaks cut (the beach north of the north mole, a creek mouth, the east bank below Santa
   Ana), and the outline cut at the mole heads. Vectorised at 1 px tolerance: 355 points.
3. **The moat** (`moat`): the tint within about 45 px outside the traced wall, less the river and the bay. **The lagoons** (`lagoons`):
   the tint north of Tondo, landward of the traced shore; islands kept as holes.

The scripts that did this worked on the scan, which is not in the repository; their results are the picks. To do it again, fetch the
scan, and follow the steps above.
