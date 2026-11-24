"""23 Nov 2026 (Morgan, session 2 of the HIST 340 work): a Hypotheses sheet in each war's workbook, in place of Conflicts.

  python3 pipeline/hypotheses_2026_11_23.py

One row per disputed point: the question, the competing readings (A, B, C), the evidence for the reading the playback follows and the
evidence against it (each item: source id, where in it, what it says), the reading adopted, how sure that is, who decided and when, the
rows it touches, what would settle it, and the history: everything the Conflicts row said, column by column, so nothing is lost.
Every Conflicts row is carried over under its own id (C01, TC01, YC01, C-PW1, C-LZ1 ...); then the Conflicts sheet is removed.

New evidence read for this pass (23 Nov 2026):
- Official Records, Series I, Vol. 27, Part 1 (S62; Morgan's HathiTrust PDF, page images read): Calef pp. 1030-1031, Buford p. 927,
  Gamble p. 934, Wadsworth pp. 265-266, Dawes pp. 275-276.
- Elliott, The New Jersey Campaign (S59; Morgan's PDF, whose printed page numbers are the PDF's): every page cited in the Trenton rows was
  checked. Five citations of 17 Nov were one page early (41, 46, 47 and 48 for 42, 47, 48 and 49); the evidence below gives the right page
  and says where it was corrected.
- Ypres, 1914 (S41; the Internet Archive copy ypres1914officia00schwuoft, read through its text with the page numbers of its running
  heads, which may be one page out): pages for the quotations the Ypres rows rest on.
Not read: Hamilton (S42) could not be opened this pass, so its quotations keep the wording recorded on 18 Nov, without pages.
"""
import os, re, sys
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = os.path.join(ROOT, 'data', 'WarMapper battle data')
TODAY = '2026-11-23'
COLS = ['hypothesis_id', 'battle_id', 'question', 'reading_a', 'reading_b', 'reading_c', 'evidence_for', 'evidence_against',
        'adopted_reading', 'adopted_because', 'confidence', 'status', 'decided_by', 'decided_on', 'reviewed_on', 'rows', 'source_ids',
        'next_step', 'history']
WIDTH = {'hypothesis_id': 9, 'battle_id': 12, 'question': 34, 'reading_a': 34, 'reading_b': 34, 'reading_c': 28, 'evidence_for': 60,
         'evidence_against': 60, 'adopted_reading': 10, 'adopted_because': 40, 'confidence': 11, 'status': 22, 'decided_by': 14,
         'decided_on': 11, 'reviewed_on': 11, 'rows': 18, 'source_ids': 16, 'next_step': 40, 'history': 70}
WHAT = {'hypothesis_id': 'Its id (the Conflicts id it came from)', 'reading_a': 'The first reading. B and C are the others; C may be empty',
        'evidence_for': 'Evidence for the adopted reading: source id, where in it, what it says. One item a line',
        'evidence_against': 'Evidence for the other readings, or against the adopted one, in the same form',
        'adopted_reading': 'A, B, C, a range, or none (all readings kept, none drawn as the answer)',
        'confidence': 'How sure the adopted reading is: high only where a cited source states it, else medium or low',
        'status': 'Open (a ruling is wanted), Proposed (a reading is put forward for Morgan to accept), Settled (decided), No ruling needed',
        'decided_by': 'Who chose the adopted reading: Morgan, or the pilot default that a ruling has not yet replaced',
        'rows': 'Positions, events and units the adopted reading is drawn in', 'history': 'What the Conflicts row said, column by column'}

# hypothesis id: (reading A, B, C, evidence for, evidence against, adopted, because, confidence, status, decided by, decided on, next step)
H = {
# ---------------- U.S. Civil War: Gettysburg, the first day ----------------
'C01': ("First shot about 07:30, at the picket post on the Chambersburg Pike", "First shot about 07:00", "Contact between 08:00 and 09:00, the time the reports give",
        "S14 First Shot marker: 7:30 a.m.",
        "S55 Reardon and Vossler, p. 19: the column sighted and the first shot fired about 0700; p. 20 dates the day's first phase from 0700.\n"
        "S02 Gamble, OR 27/1 p. 934: \"About 8 o'clock\" the picket reported the enemy approaching.\nS01 Buford, OR 27/1 p. 927: reports came in \"between 8 and 9 a. m.\"\n"
        "S62 Calef, OR 27/1 p. 1030: the enemy reported advancing \"about 8 a. m.\"",
        'A', "The reports give the time word reached each headquarters, which comes after the first shot; watches were not set together. Morgan accepted 07:30 before S55 was read.",
        'medium', 'Open', 'Morgan', '2026-11-12', "Rule on S55's 0700 against the marker's 7:30."),
'C02': ("At the First Shot marker, about 3 miles from Gettysburg", "Farther west: 3 miles from the camp near Cashtown, about 5 miles out", "On 30 June the pickets were about 4.5 miles out",
        "S07 A. P. Hill, OR 27/2 p. 607: \"About 3 miles from Gettysburg\".\nS14 First Shot marker, on the pike at Knoxlyn Road.",
        "S06 Shepard, OR 27/2: advanced \"about 3 miles\" from camp, then the pickets fell back \"about 3 miles\".\nS01 Buford, OR 27/1 pp. 926-928: enemy pickets on 30 June \"about 4½ miles from Gettysburg\".\nS11 tablet: marched about six miles.",
        'A', "Shepard may describe an earlier brush with vedettes farther west; the marker fits Hill.", 'medium', 'Settled', 'Morgan', '2026-11-12', ''),
'C03': ("Lines on Herr Ridge 09:00 to 09:30; across Willoughby Run about 10:00", "Halt on Herr's Ridge about 10:00, attack over the run about 10:15", "Davis in line of battle about 10:30",
        "S18 Bachelder map: Archer's, Davis's and Gamble's lines all labelled \"9 A.M.\"; Davis east of the run \"10.15 A.M.\".\nS11, S12 tablets: both brigades crossed Willoughby Run about 10 a.m.\n"
        "S62 Wadsworth, OR 27/1 p. 265: his division struck the Cashtown road \"at about 10 a. m.\", and (p. 266) the right was engaged before its line was formed: the Confederate attack was already moving at 10.",
        "S55 Reardon and Vossler, pp. 19-20: Archer halts on Herr's Ridge about 1000; Reynolds's leading division arrives about 1015.\nS05 Davis, OR 27/2 p. 649: line of battle \"About 10.30 o'clock\".\nS04 Heth, OR 27/2 p. 637: still uninformed of the force ahead at \"9 o'clock\".",
        'A (09:00 to 09:30 held as a range)', "The map and the tablets agree; Wadsworth's 10 a.m. arrival under fire fits an attack begun before 10.", 'low', 'Open', 'Morgan', '2026-11-12',
        "Rule between the map (9 A.M.) and S55 (about 1000). Heth's, Archer's and Davis's reports in OR 27/2 would narrow it."),
'C04': ("On Herr Ridge, about 2 miles from the town", "Within a mile of the town", '',
        "S18 map, measured: Herr Tavern 2.97 km (1.85 miles) from the square; Archer's line about 1.74 miles.\nS05 Davis, OR 27/2 p. 649: artillery opened \"within about 2 miles from town\".\nS55 Reardon and Vossler, p. 19: the halt on Herr's Ridge, two miles west of Gettysburg.",
        "S04 Heth, OR 27/2 p. 637: \"within a mile of Gettysburg\".\nS12 tablet: the line formed west of Herr's Tavern, where the map draws Archer and Davis 185 to 220 m east of it.",
        'A', "Three sources and the map agree; Heth's mile does not fit the ground.", 'medium', 'Proposed', 'pilot default', '', "Accept A and close. The tablet-versus-map point (west or east of the tavern) stays open."),
'C05': ("Main line on the eastern arm of McPherson Ridge, about 540 m from the seminary", "About 1 mile in front of the seminary", "The map's bars show the line after the fall-back of about 200 yards; the first line was out at Calef's guns",
        "S18 map: the four regiments (\"Morning\", \"9 A.M.\") on the eastern arm of the ridge.\nS09 tablet and S15 memorial stand on McPherson Ridge.\nS55 Reardon and Vossler, p. 19: Buford's last line was on McPherson's Ridge.",
        "S02 Gamble, OR 27/1 p. 934: \"in line of battle about 1 mile in front of the seminary\", then \"compelled to fall back about 200 yards to the next ridge\".\n"
        "S62 Calef, OR 27/1 p. 1030: his guns went \"about 600 yards in front of\" the position held during the night.",
        'A', "The map, the tablet and S55 agree on the ridge. Gamble's 200-yard fall-back keeps reading C alive.", 'medium', 'Open', 'pilot default', '', "Decide between A and C: whether P04 is the first line or the line after the fall-back."),
'C06': ("Calef's battery fired the opening gun, from Lt. Roder's section on the pike", "Marye's battery fired the first cannon shot, from west of Herr's Tavern", '',
        "S62 Calef, OR 27/1 p. 1031: \"Lieutenant Roder now fired the first gun (which opened the sanguinary battle of Gettysburg)\".\nS15 Buford memorial: the opening gun was Calef's.",
        "S13 tablet, Marye's battery: claims the first shot.\nS18 map prints both claims (\"Opening Guns of the Battle\" by Marye, \"Opening Gun of the Battle\" by Calef).",
        'none', "Both batteries are placed; the playback does not name the first gun.", 'low', 'No ruling needed', 'pilot default', '', "Calef's own claim is now read; a Confederate report (Pegram's battalion) would give the other side's."),
'C07': ("Left section First Sgt. Newman, centre Sgt. Pergel, right Lt. Roder", "Left Pergel, centre Newman, right Roder", '',
        "S62 Calef, OR 27/1 p. 1031: he placed \"First Sergeant Newman, commanding left section, on immediate left of road, and Sergeant Pergel, commanding center section, still farther to the left\"; Roder's section was on the right of the road.\nS08 tablet: the centre section under Pergel.",
        "S17 forum thread: left Pergel, centre Newman, right Roder.",
        'A', "Calef's own report names each section's commander.", 'high', 'Proposed', 'pilot default', '', "Accept A and close. P10 to P12 already name each section by its commander, so no position changes."),
'C08': ("About 08:00 to 10:15-10:40: \"more than two hours\"", "About 07:00 to 10:15, over three hours counting the delaying action from Marsh Creek", '',
        "S01 Buford, OR 27/1 p. 927: the First Brigade \"held its own for more than two hours\".\nS02 Gamble, OR 27/1 p. 934: \"several hours\".\nS10 tablet (Devin): over two hours.",
        "S55 Reardon and Vossler, p. 20: the cavalry's fight ran from 0700 to about 1015.",
        'A', "The two differ mainly in when the fight is counted from (see C01).", 'medium', 'Open', 'pilot default', '', "Settles with C01."),
'C09': ("Reynolds was killed by a bullet", "He was killed by one of Pegram's first shells", '',
        "S55 Reardon and Vossler, p. 22: killed instantly by a bullet as he sent the Iron Brigade into the woodlot.",
        "S04 Heth, OR 27/2 p. 637 ff.: \"One of the first shells fired by Pegram mortally wounded Major-General Reynolds\".",
        'A', "Heth was not where Reynolds fell; S55 gives the cause the other accounts give.", 'medium', 'Proposed', 'pilot default', '', "Close: the playback does not use Heth's account."),
'C10': ("Gordon at the knoll 15:00; Hays and Hoke near the town 15:45", "Gordon strikes about 15:30; the Eleventh Corps withdraws at 16:00", '',
        "S18 map: Gordon's line at the knoll \"3 P.M.\", Hays's and Hoke's lines \"3.45 P.M.\".\nS55 Reardon and Vossler, p. 26: the attack was under way before Lee's general assault of about 1600.",
        "S16 timeline: Gordon hits the Union right at 3:30 p.m.\nS62 Wadsworth, OR 27/1 p. 266: Schurz fell back \"about 2.30 p. m.\"; Wadsworth ordered his division to retire at 3.45.",
        'A', "The map is the only source read that times each brigade.", 'low', 'Open', 'pilot default', '', "Read Early (S58, OR 27/2 p. 468) and Gordon (OR 27/2)."),
'C11': ("About 14:30 to 15:00", "About 14:00", '',
        "S49: \"about 2:30 P.M.\".\nS16: Pettigrew attacks at 3:00 p.m.\nS18 map: Biddle changes position \"2.30 P.M.\"; Meredith's line \"10.15 A.M. - 3 P.M.\".",
        "S55 Reardon and Vossler, p. 23: the third phase begins around 1400 with Heth's two fresh brigades.",
        'Range 14:00 to 15:00 on the event; rows 14:30 to 15:00', "Three sources give three times; the range keeps them all.", 'low', 'Open', 'pilot default', '', "Read Heth's and Pettigrew's brigade reports for the afternoon (OR 27/2)."),
'C12': ("About 10:15", "About 10:50", '',
        "S62 Wadsworth, OR 27/1 p. 266: the right was engaged before the line was formed, \"and at this time (about 10.15 a. m.) our gallant leader fell\".\nS18 map: the Iron Brigade's line, which he was placing, from \"10.15 A.M.\".\nS55 Reardon and Vossler, pp. 21-22: killed moments after the Iron Brigade came up.",
        "S16 timeline: 10:50 a.m.",
        'Range 10:15 to 10:50, shown at 10:25', "Wadsworth, his division commander, gives about 10.15; the range is kept until Morgan rules.", 'medium', 'Proposed', 'pilot default', '',
        "Narrow the event to 10:15 to 10:30 on Wadsworth's report (new evidence, 23 Nov 2026)."),
'C13': ("About 10:30", "Later in the late morning, ending about 12:00", "Over by 11:30",
        "S18 map: the charge of the 95th New York, 14th Brooklyn and 6th Wisconsin labelled \"10.30 A.M.\".",
        "S55 Reardon and Vossler, pp. 21-23: the charge came after Reynolds's death; the second phase ran from about 1030 to 1200.\nS16: the morning attack over by 11:30.\n"
        "S62 Dawes, OR 27/1 pp. 275-276: no clock time; the 6th Wisconsin was sent from reserve to the right after the line there was forced back, and charged the cut from the pike fence.\n"
        "S62 Wadsworth, OR 27/1 p. 266: the charge followed Cutler's fall-back, after Reynolds fell about 10.15.",
        'A for the rows; the event holds 10:30 to 12:00', "The map is the only clock time; the order of events allows any time after about 10:20.", 'low', 'Open', 'pilot default', '', "Davis's report (OR 27/2 pp. 648-650) and Fowler's (OR 27/1) would narrow it."),
# ---------------- Revolutionary War: Trenton ----------------
'TC01': ("Shortly after 07:30", "08:00", "About 07:45",
         "S21 Stryker, quoting Lt. Piel: \"shortly after half past seven\".\nS61: about 7:30.\nS22, p. 10: shortly before eight o'clock.",
         "S20 Washington to Hancock: the upper division reached the post \"exactly at eight OClock\".\nS34 CDB90: 08:00.\nS59 Elliott, p. 45: both columns reached their starting points around 0800.\nS21 Stryker: about 7:45, \"nearly eight o'clock\".",
         'Range 07:30 to 08:00', "The sources spread over half an hour; the range keeps them all.", 'medium', 'Open', 'pilot default', '', ''),
'TC02': ("At Birmingham, about 06:00", "At Birmingham, at 07:00", "At Bear Tavern",
         "S59 Elliott, p. 44: about two hours from the start of the march (04:00) to Birmingham.\nS63 driving tour: 6 a.m.\nS22, pp. 8-9: Birmingham, after weighing Bear Tavern.",
         "S29 marker: the split at Birmingham at 7 AM.\nS22, pp. 8-9: some historians put it at Bear Tavern.\nS20, note 6: the upper division halted near the picket about 7 a.m. (kept as T05).",
         'A', "Two modern accounts and the march times agree.", 'medium', 'Proposed', 'Morgan', '2026-11-18', "Close."),
'TC03': ("The whole jäger company, about 50", "A sergeant and 15 men", '',
         "S36 Wiederhold's sketch, legend F: one officer and 50 jägers.\nS59 Elliott, p. 44: a company of jaegers at the Hermitage.\nS61: about 50 under Lt. von Grothausen.",
         "S21 Stryker gives both \"a commissioned officer and fifty men\" and \"a sergeant and fifteen men\".",
         'none (both on the unit record)', "The evidence leans to A.", 'low', 'Open', 'pilot default', '', "Adopt A on the unit record."),
'TC04': ("About an hour", "About ninety minutes, 08:00 to 09:30", "About two hours",
         "S59 Elliott, p. 49 (cited as p. 48 on 17 Nov): \"The battle lasted only an hour.\"",
         "S34 CDB90: 08:00 to 09:30.\nS23 tour script: over by 10 a.m.\nS21 Stryker, the Lossberg quartermaster: the regiment defended about two hours.",
         'Range: the surrender rows end between 08:45 and 10:00', "The rows' ranges cover all three.", 'low', 'Open', 'pilot default', '', ''),
'TC05': ("Shortly after the others", "About an hour after the others", '',
         "S59 Elliott, p. 49 (cited as p. 48 on 17 Nov): the Knyphausen soldiers \"laid down their arms shortly after their comrades\".\nS33, citing Wood: minutes after the rest of the brigade.",
         "S21 Stryker: Biesenrodt surrendered about an hour after the other regiments.",
         'Range: T51 runs 09:00 to 10:30', "The range covers both.", 'low', 'Open', 'pilot default', '', "Narrow T51 towards A, two modern accounts against Stryker."),
'TC06': ("Garrison 1,382 effectives; 896 surrendered", "Garrison about 1,400 to 1,520", "Prisoners 909 (23 officers and 886 men), 918 or 868",
         "S59 Elliott, p. 42 (cited as p. 41 on 17 Nov): 1,382 effectives on 26 December (Rall 512, Knyphausen 429, Lossberg 345, 50 jaegers, 20 dragoons); p. 49 (cited as p. 48): 22 killed, 83 badly wounded, 896 surrendered.\nS33, citing Fischer: 896.",
         "S22, S33: about 1,400. S35 (Park Service): 1,500. S34: 1,520.\nS20 Washington: 23 officers and 886 men; the enclosed return, 918 (note 15).\nS21: 868 on the Hessian officers' list.\nS34: 996 Hessian casualties in all.",
         'none (all figures on the records)', "Counts differ by what they include (effectives, servants, the band).", 'low', 'Open', 'pilot default', '', "Adopt S59 on the battle record."),
'TC07': ("About 100", "Four officers and 82 men", "About 150",
         "S21 Stryker: three officers and 100 men.\nS61: about 100.", "S21 Stryker, elsewhere: four officers and 82 men.\nS61, Fischer's list: 150.",
         'none', "The detachment took no part.", 'low', 'No ruling needed', 'pilot default', '', ''),
'TC08': ("Line of battle on the east edge, the counter-attack into King and Queen Streets, surrender between Montgomery and Stockton at Perry Street", "To The Swamp, a bayonet attack, then the orchard", "A field outside the town, a final attack, then the orchard",
         "S36 Wiederhold's sketch: line H along today's Montgomery Street, the attack I on King and Queen Streets, the surrender ground K between Montgomery and Stockton at Perry Street.",
         "S22, p. 12: to The Swamp, north of Perry Street between Stockton and Montgomery, then a bayonet attack, then the orchard.\nS59 Elliott, p. 48 (cited as p. 47 on 17 Nov): east to the orchard, then a counter-attack north toward the Princeton road.\nS21 Stryker: the surrender in the orchard east of the Friends' Meeting House.",
         'A', "The sketch puts the three descriptions on one block: The Swamp, the orchard and K are the same ground.", 'medium', 'Proposed', 'pilot default', '', "Close: the readings describe one place."),
'TC09': ("None killed; two officers and two privates wounded; some died of exposure on the march", "Two officers and one or two privates wounded", "Two privates killed and two wounded",
         "S59 Elliott, p. 49 (cited as p. 48 on 17 Nov): none killed in action, two officers and two privates wounded, an unknown number dead of exposure.",
         "S20 Washington: two officers and one or two privates wounded.\nS20, note 9 (Tilghman): two privates killed, two wounded.\nS33, citing Fischer: two died of exposure, five wounded.\nS34 CDB90: 12.",
         'none (not used in the positions)', '', 'low', 'No ruling needed', 'pilot default', '', ''),
'TC10': ("Pennington road: an officer and 24 or 25 men", "An officer, an NCO and 19 men", '',
         "S36 sketch, A: 1 officer and 25 privates.\nS59 Elliott, p. 44: a detachment of twenty-four.\nS61: a corporal and 24 men.",
         "S21 Stryker: an officer, an NCO and 19 men. Maidenhead road: about 70 (S21) or 1 captain, 1 officer and 75 (sketch, D). Ferry: 1 officer and 27 (S21) or 30 (sketch, E).",
         'none (both on the unit records)', '', 'low', 'Open', 'pilot default', '', "Adopt A for the Pennington road picket."),
'TC11': ("Rall formed on King Street at Pinkerton's alley and counter-attacked on Queen Street; Lossberg on King Street", "Rall up King Street, Lossberg up Queen Street", '',
         "S21 Stryker: the Rall regiment formed on King Street at Pinkerton's alley, and Rall was shot on Queen Street.",
         "S33, citing Wood: Rall's regiment up King Street, Lossberg's up Queen Street.\nS59 Elliott, p. 47 (cited as p. 46 on 17 Nov): the two regiments tried to form along King and Queen Streets, without saying which was where.",
         'A', '', 'low', 'Open', 'pilot default', '', "The Hessian court of inquiry testimony, printed in Stryker (S21), should settle it."),
'TC12': ("East of Queen Street, Third Street to Front Street (the sketch's bars)", "Down King Street after the guns were taken", "Its men retook the guns on King Street; the brigade received the surrender in the orchard",
         "S36 Wiederhold's sketch: Stirling's bars (T) just east of Queen Street.",
         "S33, citing Wood: Weedon's men down King Street after the guns were taken.\nS59 Elliott, p. 47: reinforcements from Stirling's brigade retook the guns; Monroe of the 3d Virginia wounded there.\nS21 Stryker: Stirling received the surrender in the orchard.",
         'A for row T36', "A brigade could have done all three; the sketch shows one moment.", 'low', 'Open', 'pilot default', '', ''),
'TC13': ("Infantry over by about 02:00, artillery by 03:00", "Infantry by 03:00, artillery an hour later", "All over by about 04:00",
         "S60: Knox put the infantry over by about 2 a.m., the artillery by about 3.",
         "S59 Elliott, p. 43: the infantry by 0300, the artillery an hour later.\nS61: about 4 a.m.\nS22, p. 8: four o'clock.",
         'Range: event TE03 02:00 to 04:00', "All agree the march began about 04:00.", 'medium', 'Open', 'pilot default', '', ''),
'TC14': ("Toward the Princeton road, on the left", "In the centre of Greene's three columns", '',
         "S22, p. 11: Hand's riflemen and Scott's and Lawson's battalions (Stephen's Virginians) through the fields on the left to the Princeton road.",
         "S59 Elliott, p. 47 (cited as p. 46 on 17 Nov): Mercer's brigade to the west, Stephen's in the centre, Fermoy's to the east, Stirling's in reserve.",
         'A for row T28', '', 'low', 'Open', 'pilot default', '', "S59 is the Army's own history and names the order; consider moving T28 to the centre."),
'TC15': ("On Queen Street in front of Isaac Yard's house, during the attack from The Swamp", "After ordering the retreat to the orchard, when the second counter-attack failed", '',
         "S22, p. 12: shot from his horse on Queen Street in front of Isaac Yard's house.\nS21 Stryker: shot on Queen Street.",
         "S59 Elliott, p. 48 (cited as p. 47 on 17 Nov): mortally wounded just after ordering the retreat to the orchard.",
         'A for row T39', '', 'low', 'Open', 'pilot default', '', ''),
'TC16': ("Taken quickly, as Sullivan's men reached the bridge", "Held for over an hour", '',
         "S59 Elliott, p. 45: Sullivan's men took the barracks and headed for the bridge; p. 47: Glover's and St. Clair's brigades reached the bridges.",
         "S61, citing Fischer: Sgt. Müller's 18 men held the Assunpink bridge for over an hour.",
         'A: row T11 ends at 08:27', '', 'low', 'Open', 'pilot default', '', ''),
'TC17': ("345 soldiers", "467 men and 16 officers", '',
         "S59 Elliott, p. 42 (cited as p. 41 on 17 Nov): 345.", "S21 Stryker: 467 men and 16 officers.",
         'none (both on the assignment record)', "Probably effectives against the roll.", 'low', 'Open', 'pilot default', '', ''),
'TC18': ("Toward Bordentown", "Toward Princeton, after the dragoons", '',
         "S20 Washington and S21 Stryker: some down the road toward Bordentown.", "S61: they followed the dragoons, so probably toward Princeton (its inference).",
         'A for track T-HE-PKRIV (route T63)', '', 'low', 'Open', 'pilot default', '', ''),
# ---------------- World War I: First Ypres ----------------
'YC01': ("22 November (the British date)", "17 November, when the German Fourth Army gave up the offensive", "13 November (French) or 30 November (German)",
         "S44 summary: 22 November.",
         "S41, pp. 123-124: \"on the 17th November the commander of the Fourth Army decided to give up any idea of continuing the offensive\".\nS47: the French date 13 November, the Germans 30 November.\nS44 text: the Yser floods end the battle on 30 November.",
         'Range: the battle record ends 17 to 22 November; the playback runs to 22 November', "Each national history defines the battle differently.", 'medium', 'Open', 'pilot default', '', "A battle record needs room for more than one definition."),
'YC02': ("The French 17th Division (IX Corps), 23 to 24 October", "The French \"18th Corps (9th Army)\", night of 23-24 October", '',
         "S41, p. 43, British editors' note: the 2nd Division was relieved by a division of the French IX Corps.\nS44: the French IX Corps took over on 23 October.\nS40, Sketches 7 and 8: IX Corps on that front by 25 October.",
         "S42 Hamilton: relieved by the French \"18th Corps (9th Army)\" (wording recorded on 18 Nov; page not checked).",
         'A', "Hamilton wrote in 1916 without the French order of battle.", 'medium', 'Proposed', 'pilot default', '', "Close on A."),
'YC03': ("The British 3rd Division", "The 7th and 15th Brigades", "The 5th Division",
         "S41, p. 94, British editors' note: \"the 3rd Division, which had now taken over the line south of the Menin road\".\nS40, Sketch 13 (9 November): \"3rd Div.\" south of the Menin road.",
         "S42 Hamilton: the 7th and 15th Brigades (page not checked).\nS43: \"The trenches were now held by the Fifth Division (Morland's)\".",
         'A', "The 7th Brigade was of the 3rd Division and the 15th of the 5th: the relief was mixed, but the sketch names the 3rd.", 'medium', 'Proposed', 'pilot default', '', "Close on A."),
'YC04': ("German: Messines from 1 November, Wytschaete from 2 November", "Both retaken by the French at 11 a.m. on 2 November", '',
         "S41, p. 85: by 4 p.m. on 1 November the attackers reached the eastern edge of Wytschaete; fierce street fighting in Messines all day; p. 87: Wytschaete the centre of the heaviest fighting on the 2nd.\nS45: the Germans had both by the morning of 1 November.\nS40, Sketch 12 (4 November): the French line about 1 km west of Wytschaete.",
         "S42 Hamilton: \"at 11 a.m. on the 2nd, both Messines and Wytschaete were retaken by the French\" (page not checked).\nS41, p. 85, editors' note: by the afternoon of 1 November the French had taken over the defence of Wytschaete; p. 87: the credit for its defence that day belongs to the French.",
         'A', "French counter-attacks reached the villages without holding them.", 'medium', 'Open', 'pilot default', '', ''),
'YC05': ("Lost on 11 November", "Held by the Allies until December", '',
         "S41, p. 119: \"the capture of Hill 60 near ZWARTELEEN was of exceptional importance\".\nS40, Sketch 14: the French line on the afternoon of 11 November bent back north of the hill.",
         "No source read. The December date was a recollection of Claude's, recorded as such on 13 Nov.",
         'A', "The German account and the British official sketch agree.", 'medium', 'Proposed', 'pilot default', '', "Close on A."),
'YC06': ("British in the western part of the wood, Germans in the east and south", "The Guard took the whole wood on 14 November", '',
         "S41, p. 122, British editors' note: \"This statement is not true\"; the chateau fell and was retaken the same day by the 2nd King's Own Yorkshire Light Infantry.",
         "S41, p. 122: \"HERENTHAGE Wood was completely taken by the Guard on the 14th November\".",
         'A', "The British editors deny the German claim.", 'medium', 'Proposed', 'pilot default', '', "Close on A."),
'YC07': ("The 5th Bavarian Brigade took St. Eloi on 9-10 November (the German account)", "The 3rd and 26th Divisions broke through at St. Eloi on 11 November and reached Zwarteleen", "The French held about 1 km south-east of St. Eloi on 9 and 11 November",
         "S40, Sketches 13 and 14: the French line about 1 km south-east of St. Eloi on 9 and 11 November.",
         "S41, p. 103: the brigade went on \"from the heights of ST. ELOI it had just stormed\".\nS44, citing Beckett (2006): the 3rd and 26th Divisions broke through at St. Eloi on 11 November.",
         'C for the line; the German claim kept in the wording of its row', "St. Eloi and Zwarteleen are 4 km apart across the canal; S44 may run two events together.", 'low', 'Open', 'pilot default', '', "The British official history's text for 9-11 November (S40, beyond p. 176)."),
'YC08': ("29 to 31 October", "29 October to 1 November", "To 5 November",
         "S47 and S44 summary: 29 to 31 October.", "S44 section heading: to 1 November.\nS40 chapter titles: \"Battle of Gheluvelt\" through 5 November.",
         'A, with the wider dates in the notes', "A naming question, not a placing one.", 'medium', 'Settled', 'pilot default', '', ''),
'YC09': ("At Kortekeer Cabaret", "At Pilckem", '',
         "S41, p. 37, British editors' note: the Germans captured the Kortekeer Cabaret, and the Queen's retook it.\nS40, S44, S47: Kortekeer Cabaret.\nS40, Sketch 7: the line of 23 October through Kortekeer.",
         "S42 Hamilton: the 1st Brigade was attacked \"at Pilkem\" (page not checked).",
         'A', "Hamilton names the nearest village, the others the inn on the road a mile north of it.", 'medium', 'Proposed', 'pilot default', '', "Close on A."),
'YC10': ("At Staden on 19 October", "Close to Staden on the 19th; Staden taken on the 20th", '',
         "S40, summarising the German account: it reached Staden.",
         "S41, p. 33: \"STADEN was finally surrounded and taken by the 46th Reserve Division.\"",
         'A, with a note', "A day's difference at division level.", 'low', 'Open', 'pilot default', '', "Follow S41 (the German account itself): place the row of the 19th short of Staden."),
'YC11': ("Back in line on 25 October", "Still in reserve on 25 October", "In line by 29 October",
         "S42 Hamilton: \"came up on the right of the 2nd Division\" on 25 October (page not checked).",
         "S40, Sketch 8 (25 October): still a reserve between Ypres and Zillebeke.\nS40, Sketch 9: in line east of Polygon Wood by 29 October.",
         'Range: the row in line starts 25 to 27 October', '', 'low', 'Open', 'pilot default', '', "Read S40's text for 24-27 October."),
'YC12': ("The French line about 2.5 km north of Het Sas on 11 November", "The Germans close up to Het Sas on 10 November", '',
         "S40, Sketch 14: the French line from the canal near Steenstraat past Kortekeer on 11 November; the line of the 10th a few hundred metres north.",
         "S41, p. 109: \"the 44th Reserve Division pushed forward till close up to HET SAS\".",
         'A for the French line; German rows keep the places their account names', "\"Close up to\" may mean the canal bank at Steenstraat.", 'medium', 'Open', 'pilot default', '', "The French official history would settle it."),
# ---------------- Philippine War: Manila and Luzon 1899 ----------------
'C-PW1': ("The roster: King with the 4th Cavalry, 14th Infantry and 1st California; Ovenshine with Washington, Idaho and North Dakota", "Otis on 5 February: King's swing by the Californias, Washingtons and Idahos; Ovenshine's line North Dakota, 14th Infantry and 4th Cavalry", '',
          "S66 roster (January 1899).", "S65 Otis, on 5 February.",
          'A until 3 February, B from 4 February', "The brigades were evidently reorganised between January and the battle.", 'medium', 'Open', 'pilot default', '', "A general order of late January would settle it."),
'C-PW2': ("At El Deposito (the reservoir) at the close of 5 February", "At the waterworks", '',
          "S65 Otis: the Nebraskans and a Tennessee battalion \"captured the powder house and Deposito\"; Otis had wired \"Waterworks must wait\".",
          "S64 index: 1st Neb. \"Waterworks\".",
          'A', "The waterworks (pumping station) were taken after this playback ends.", 'medium', 'Open', 'pilot default', '', ''),
'C-PW3': ("\"Former\" labels are before the battle; heavy double-dashed lines named for regiments are final positions", "(no other reading in a source)", '',
          "S64: title \"positions prior to the battle of 5 Feb and after the capture of Caloocan, 10 Feb\"; the named heavy lines match the index of final positions.",
          "S64: no legend found on the sheet.",
          'A', '', 'low', 'Open', 'pilot default', '', "Find the sheet's legend or a description of it."),
'C-LZ1': ("20 October", "22 October", '',
          "S74 Otis: \"October 20, the day upon which General Lawton's troops had seized San Isidro\".", "S68: \"San Isidro was recaptured October 22\".",
          'A', "Otis's report is primary; the pamphlet is later.", 'medium', 'Open', 'pilot default', '', ''),
'C-LZ2': ("Left Tarlac on the night of the 13th", "Already at Bayambang about 12 November", "Left Tarlac on 1 November for Bayombong",
          "S74 (Buencamino, captured 21 Nov): \"Buencamino and Aguinaldo on night 13th\" left Tarlac.",
          "S68, printing MacArthur's 1900 report: a council at Bayambang \"about November 12\" and a decree \"Given at Bayambang, November 12, 1899\".\nS74 (rumour, 8 Nov): left Tarlac 1 November for Bayombong.",
          'At Tarlac until the 12th, Bayambang on the 13th', '', 'low', 'Open', 'pilot default', '', ''),
'C-LZ3': ("26 November", "24 November", '',
          "S75 Parker, on the spot (\"Vigan, November 26 - 1 p. m.\"): war ships shelled the trenches that morning and landed 200, who occupied the town.",
          "S74 Otis: \"Vigan, which place Navy occupied 24th instant\".",
          'A', "The eyewitness, writing that day.", 'medium', 'Open', 'pilot default', '', ''),
'C-LZ4': ("7 November", "9 November", '',
          "S68: 7 November.\nS74 (8 Nov): \"Wheaton should have landed at San Fabian yesterday\".",
          "S74 (10 Nov): \"He secured lodgment yesterday at San Fabian\".",
          'A', "The landing began on the 7th; the lodgment may have been secured on the 9th.", 'low', 'Open', 'pilot default', '', ''),
}
SETTLED_LINN = {   # settled on 22 Nov 2026 at Morgan's choice: Linn (S80) followed
'C-LZ5': ("At Tayug about 14 November", "By 11-13 November", "S80 Linn, p. 148: San Jose on the 12th, Umingan on the 13th, then the cavalry to Tayug and San Nicolas.", "S74, S68: by 11-13 November."),
'C-LZ6': ("The San Nicolas-Tayug area", "Binalonan about noon", "S80 Linn, p. 148: the San Nicolas-Tayug area on the 16th.", "S75 (Batson): Young reached Binalonan about noon on the 16th."),
'C-LZ7': ("Naguilian, La Union", "Tubao, with about 400 soldiers", "S80 Linn, p. 154: reached Naguilian on the 17th.", "S75: at Tubao with about 400 soldiers."),
'C-LZ8': ("Outside Namacpacan", "Trenches at Tagudin", "S80 Linn, p. 155: outside Namacpacan.", "S68 (Young's report): trenches at Tagudin."),
'C-LZ9': ("About 700 under Juan and Blas Villamor", "Tinio", "S80 Linn, p. 157: about 700 under the Villamors; Tinio's men attacked Vigan that night.", "S74: a telegram names Tinio wounded, from which he had been inferred."),
'C-LZ10': ("18 November", "19 November", "S80 Linn, p. 153: 18 November.", "S74: 19 November."),
'C-LZ11': ("By train some twenty miles north, then twelve miles east across country", "Via Urdaneta, Manaoag and Pozorrubio", "S80 Linn, p. 148: by train some twenty miles north, then twelve miles east across country.", "S68: \"via Urdaneta, Manaoag and Pozorubio\"."),
'C-LZ12': ("About 1 November, after Santa Rosa on the 28th and a three-day halt", "30 October, Aliaga on the 31st", "S80 Linn, pp. 146-147: Santa Rosa on the 28th, a three-day halt, then Cabanatuan.", "S74: 30 October, Aliaga on the 31st."),
}
for k, (a, b, f, g) in SETTLED_LINN.items():
    H[k] = (a, b, '', f, g, 'A', "Linn (S80) followed, at Morgan's choice.", 'medium', 'Settled', 'Morgan', '2026-11-22', '')
H['C-LZ11'] = H['C-LZ11'][:6] + ("Linn's timing; S68's path, since S80 names no stations.",) + H['C-LZ11'][7:]
H['C-PW4'] = ("One Filipino soldier, approaching and refusing to halt; Otis does not say he was hit", "Two Filipino soldiers shot and killed", '',
              "S65 Otis, p. 161: \"an insurgent approaching the picket and refusing to halt or answer when challenged\"; \"our picket discharged his piece\".",
              "S82 Wolff (1960): Grayson \"shot and killed two Filipino soldiers\".",
              'A', "Otis followed; the picket is named Grayson on S82, which Otis does not contradict.", 'medium', 'Settled', 'Morgan', '2026-11-22', '')

IDS = re.compile(r'\b(?:[A-Z]{1,3}\d{2,3}[a-z]?|LZ\d{3}|[MT]\d{2,3}|T-[A-Z0-9-]+)\b')


def main():
    files = sorted(f for f in os.listdir(FOLDER) if f.endswith('.xlsx') and f != 'Sources and notes.xlsx')
    done = set()
    for f in files:
        path = os.path.join(FOLDER, f); wb = openpyxl.load_workbook(path)
        old = wb['Conflicts']; head = [c.value for c in old[1]]
        rows = [dict(zip(head, [c.value for c in r])) for r in old.iter_rows(min_row=2) if r[0].value]
        at = wb.sheetnames.index('Conflicts'); ws = wb.create_sheet('Hypotheses', at); wb.remove(old)
        bold = Font(bold=True); fill = PatternFill('solid', fgColor='DDEBF7'); wrap = Alignment(wrap_text=True, vertical='top')
        for c, name in enumerate(COLS, 1):
            x = ws.cell(1, c, name); x.font = bold; x.fill = fill; x.alignment = wrap
            ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width = WIDTH[name]
        for i, r in enumerate(rows, 2):
            k = r['conflict_id']; assert k in H, 'no hypothesis written for ' + k
            a, b, c, ef, ea, ad, why, conf, st, by, on, nxt = H[k]
            hist = '\n'.join('%s: %s' % (h, str(v).strip()) for h, v in r.items() if h not in ('conflict_id', 'battle_id', 'question', 'status') and v not in (None, ''))
            hist = ('Status in Conflicts: %s\n' % r['status']) + hist
            said = str(r.get('how the pilot handled it') or '') + ' ' + ' '.join(str(v) for h, v in r.items() if h.startswith('v') and v)
            span = lambda m: ' '.join('%s%0*d' % (m.group(1), len(m.group(2)), n) for n in range(int(m.group(2)), int(m.group(3)) + 1))
            said = re.sub(r'\b([A-Z]{1,3})(\d{2,3}) to \1?(\d{2,3})\b', span, said)          # "P10 to P12", "P20 to P23"
            used = sorted(set(IDS.findall(said)) - {k}, key=lambda u: (re.sub(r'\d', '', u), int(re.sub(r'\D', '', u) or 0)))
            used = [u for u in used if not re.fullmatch(r'S\d+|C\d+|TC\d+|YC\d+|K\d+', u)]
            src = sorted(set(re.findall(r'\bS\d{2}\b', ef + ' ' + ea)), key=lambda s: int(s[1:]))
            vals = [k, r['battle_id'], r['question'], a, b, c or None, ef, ea, ad, why or None, conf, st, by, on or None, TODAY, '; '.join(used) or None,
                    '; '.join(src) or None, nxt or None, hist]
            for j, v in enumerate(vals, 1): ws.cell(i, j, v).alignment = wrap
            done.add(k)
        ws.freeze_panes = 'D2'
        if rows: ws.auto_filter.ref = 'A1:%s%d' % (openpyxl.utils.get_column_letter(len(COLS)), len(rows) + 1)
        for col, opts in (('K', 'high,medium,low'), ('L', 'Open,Proposed,Settled,No ruling needed')):
            dv = DataValidation(type='list', formula1='"%s"' % opts, allow_blank=True); dv.add('%s2:%s%d' % (col, col, len(rows) + 300)); ws.add_data_validation(dv)
        rm = wb['Read me']                       # the count of disputed points now counts this sheet
        for row in rm.iter_rows():
            for x in row:
                if isinstance(x.value, str) and 'Conflicts!' in x.value: x.value = x.value.replace('Conflicts!', 'Hypotheses!')
        rm.append([]); rm.append(['Hypotheses (23 Nov 2026)', 'One row per disputed point, in place of the Conflicts sheet: the question, the readings (A, B, C), the evidence for and against the reading the playback follows, each item with its source and page, the reading adopted, how sure it is, who decided and when, the rows it touches and what would settle it. The history column keeps everything the Conflicts row said. Status: Open (a ruling is wanted), Proposed (a reading is put forward for Morgan to accept), Settled, No ruling needed.'])
        rm.cell(rm.max_row, 2).alignment = wrap
        wb.save(path)
        print(f, len(rows), 'hypotheses')
    assert done == set(H), 'written but no Conflicts row: %s' % (set(H) - done)
    sh = os.path.join(FOLDER, 'Sources and notes.xlsx'); wb = openpyxl.load_workbook(sh); rm = wb['Read me']
    shifted = [m for m in list(rm.merged_cells.ranges) if m.min_row >= 4]       # insert_rows leaves merged cells behind: move them by hand
    for m in shifted: rm.unmerge_cells(str(m))
    heights = {r: rm.row_dimensions[r].height for r in range(4, rm.max_row + 1) if rm.row_dimensions[r].height}
    rm.insert_rows(4, 3)
    for m in shifted: rm.merge_cells(start_row=m.min_row + 3, start_column=m.min_col, end_row=m.max_row + 3, end_column=m.max_col)
    for r in range(4, rm.max_row + 1): rm.row_dimensions[r].height = None
    for r, h in heights.items(): rm.row_dimensions[r + 3].height = h
    rm.cell(4, 1, 'What changed on 23 November 2026 (later): Hypotheses in place of Conflicts').font = Font(bold=True)
    rm.cell(5, 1, 'Each war\'s workbook has a Hypotheses sheet in place of Conflicts: one row per disputed point, with the competing readings, the evidence '
                  'for and against the adopted one (source and page), the adopted reading, its confidence, who decided and when. All 59 Conflicts rows are carried '
                  'over under their own ids, with their old text in a history column. New evidence: Calef, Buford, Gamble, Wadsworth and Dawes (Official Records, '
                  'vol. 27, pt. 1, S62) and the German account of Ypres (S41) with page numbers. Elliott (S59) was checked page by page: five Trenton citations of '
                  '17 Nov were one page early (pp. 41, 46, 47, 48 should be 42, 47, 48, 49); the Hypotheses give the right pages. The same slip may be in '
                  'the Positions rows that cite S59 (see Gaps).').alignment = Alignment(wrap_text=True, vertical='top')
    rm.merge_cells('A5:D5'); rm.row_dimensions[5].height = 120
    wb.save(sh)
    rw = os.path.join(FOLDER, 'Revolutionary War.xlsx'); wb = openpyxl.load_workbook(rw)   # a Trenton gap: it goes in that war's workbook
    g = wb['Gaps']; gh = [c.value for c in g[1]]
    new = {'gap_id': 'G-S59', 'battle_id': 'TREN', 'gap': 'Elliott (S59) page numbers in the Positions and Events rows may be one page early',
           'effect on the data': 'Checked on 23 Nov 2026 against the PDF (its printed page numbers are the PDF\'s): five citations in the Trenton disputes were one page early. The Positions, Events and Units rows that cite S59 by page were not checked.',
           'how to close it': 'Check every S59 page cited in the Revolutionary War workbook against the PDF in Historical Info and correct it.', 'status in v2': 'Open.'}
    g.append([new.get(h) for h in gh])
    wb.save(rw)


if __name__ == '__main__':
    main()
