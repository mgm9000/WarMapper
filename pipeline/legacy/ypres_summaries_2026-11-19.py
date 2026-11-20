"""19 Nov 2026 (Morgan): pause at the end of each day (and week) with a summary of the day's events.
Adds the Summaries sheet and First Ypres' daily and weekly summaries. Each one is written only from the workbook's own
position rows and events for that day (activity and place columns), and cites the sources those rows cite. Where the rows
record no change, the summary says so rather than filling the gap."""
import openpyxl
from openpyxl.styles import Font, Alignment
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'
D = [
 ('1914-10-18', 'The Allies push east', 'The British 7th Division wheels forward towards Menin, and the British cavalry probe the Lys crossings without getting over. French cavalry push out to Roulers. On the coast the German III Reserve Corps attacks the Belgian line on the Yser, while two new German reserve corps march up behind it.', 'S40; S41; S45'),
 ('1914-10-19', 'The encounter', 'Four new German reserve corps strike the Allied cavalry screen. Roulers falls, the French cavalry are driven back towards Passchendaele and Houthulst, and the British 3rd Cavalry Division takes Ledeghem but falls back. The 7th Division gives up its attack on Menin, falls back and digs in from Zandvoorde to Zonnebeke.', 'S40; S41'),
 ('1914-10-20', 'The ridge lost', 'The Germans take Passchendaele and Becelaere and clear Houthulst Forest, and the French cavalry are forced back behind it. The British I Corps arrives: the 2nd Division puts out outposts north-east of Ypres and the 1st Division marches up. French Territorials hold Bixschoote and the canal. In the north, the XXII Reserve Corps closes round Dixmude.', 'S40; S41'),
 ('1914-10-21', 'I Corps halted', "Haig's attack towards Poelcappelle and Langemarck is stopped in the afternoon; the 1st and 2nd Divisions entrench north and north-east of Ypres. The 7th Division draws its left back from Zonnebeke. In the south, dismounted German cavalry take Kortewilde from the British cavalry, who hold from Messines to the canal; the 4th Division extends its line to the Douve. The French cavalry withdraw behind the canal.", 'S40; S41; S42; S43; S44; S47'),
 ('1914-10-22', 'Kortekeer Cabaret', 'The German 46th Reserve Division attacks the line from Bixschoote to Langemarck and breaks in at Kortekeer Cabaret. Mass attacks on Langemarck fail.', 'S40; S41'),
 ('1914-10-23', 'The French come in', 'The British retake Kortekeer Cabaret. The French 17th Division takes over from the British 2nd Division east of Langemarck, and the 2nd Division moves south to hold Polygon Wood and the Zonnebeke road.', 'S40; S42; S44; S47'),
 ('1914-10-24', 'Across the Yser', 'French Territorials relieve the British 1st Division, which goes into reserve. On the coast the German III Reserve Corps crosses the Yser between St. Georges and Tervaete; the Belgians fall back to the railway embankment, and the French 42nd Division is sent to the centre of their line.', 'S40; S41; S42; S44; S47'),
 ('1914-10-25', 'The Kruiseik salient', 'The British 1st Division comes back into line between the 2nd and 7th Divisions, astride the Menin road. The 7th Division holds the salient at Kruiseik. North of Ypres the French 17th Division, the Territorials and the French cavalry hold the line from the canal to Zonnebeke.', 'S40; S42; S44; S47'),
 ('1914-10-26', 'Kruiseik taken', 'German cavalry and the XXVII Reserve Corps take Kruiseik from the 7th Division.', 'S40; S41'),
 ('1914-10-27', 'A line west of Kruiseik', 'The 7th Division re-forms on a line west of Kruiseik, from the Menin road cross-roads to north of Zandvoorde.', 'S41; S42'),
 ('1914-10-28', 'Reserves gather', 'No change of position on record. Behind the German line the 6th Bavarian Reserve Division is held as army reserve at Dadizeele.', 'S41'),
 ('1914-10-29', 'Cross-roads lost', 'A dawn attack in fog takes the cross-roads south-east of Gheluvelt; the 1st Division forms a new line across the Menin road east of the village and the 7th Division is driven back on Gheluvelt. The new German XV Corps assembles behind the cavalry. In the north, the French IX Corps holds from Poelcappelle to the Broodseinde cross-roads.', 'S40; S41; S42; S43; S44'),
 ('1914-10-30', 'Fabeck attacks', 'The new German army group attacks south of the Menin road. Zandvoorde falls and the British cavalry are driven off its ridge; the 7th Division turns its right back, and Bulfin\'s force fills the gap at Klein Zillebeke. The Bavarians take Hollebeke and the Germans close on Messines. On the coast the Belgians flood the Yser plain.', 'S41; S42; S43; S44'),
 ('1914-10-31', 'Gheluvelt', 'Gheluvelt falls about 1.30 p.m. The 2nd Worcestershire retake it, and the line is re-formed in front of Veldhoek. Messines is stormed, and the British cavalry hold on in the village and at Wytschaete. French detachments take over between the canal and St. Eloi. On the coast the German III Reserve Corps withdraws behind the Yser as the floods rise.', 'S40; S41; S42; S43; S44; S45'),
 ('1914-11-01', 'Messines ridge lost', 'Messines and Wytschaete pass to the Germans; the British cavalry are withdrawn behind the French, and the French XVI Corps takes over west of the ridge. Cavan\'s force holds at Klein Zillebeke with the French on its right.', 'S41; S42; S43'),
 ('1914-11-02', 'Wytschaete', 'The 6th Bavarian Reserve Division takes Wytschaete, and the German 3rd Division comes into line between Wytschaete and Messines. The XV Corps makes slow progress in the woods south of the Menin road.', 'S40; S41'),
 ('1914-11-03', 'Attacks at Langemarck', 'The German III Reserve Corps opens its main attack on either side of Langemarck.', 'S40; S41; S44'),
 ('1914-11-04', 'The line holds', 'The Allied line stands from the canal north of Ypres, round the east of the town past Polygon Wood and Veldhoek, to Klein Zillebeke, and on through French-held St. Eloi and west of Wytschaete to the Douve.', 'S40; S41; S42; S43; S44'),
 ('1914-11-05', '7th Division relieved', 'Brigades of the British II Corps take over from the worn-out 7th Division south of the Menin road; the 7th goes back to rest. A German attack on Langemarck fails.', 'S40; S41; S42; S43'),
 ('1914-11-06', 'Klein Zillebeke', 'The Germans take Klein Zillebeke. The French give way on Cavan\'s right; the British 3rd Cavalry Division counter-attacks at Zwarteleen and the line is restored west of Klein Zillebeke.', 'S41; S42; S43'),
 ('1914-11-07', 'Reforming', 'The French detachment that gave way the day before re-forms on the right of the British, from Hill 60 to the canal bank.', 'S42'),
 ('1914-11-08', 'Quiet on record', 'No change of position on record.', ''),
 ('1914-11-09', 'The Guard comes in', 'The German line is reorganised for a new attack: Winckler\'s Guard Division comes into line north of the Menin road, the 4th Division south of it, and the XXVII Reserve Corps shortens its front. The French 31st Division is in line north of the canal on Cavan\'s right.', 'S40; S41'),
 ('1914-11-10', 'Dixmude and St. Eloi', 'Dixmude falls and the French naval brigade is driven across the Yser. North of Ypres the Germans reach the canal, and the Bavarians take St. Eloi.', 'S40; S41'),
 ('1914-11-11', 'Nonne Bosschen', 'The Prussian Guard breaks through north of the Menin road, reaches Nonne Bosschen and is driven out; the 1st Division\'s line is restored a little further back. The II Corps brigades are pressed back in Herenthage wood, and an attack on Polygon Wood fails.', 'S40; S41; S42; S43'),
 ('1914-11-12', 'After the Guard', 'No change of position on record; the line stands where the Guard\'s attack left it.', ''),
 ('1914-11-13', 'No change on record', 'No change of position on record.', ''),
 ('1914-11-14', 'No change on record', 'No change of position on record.', ''),
 ('1914-11-15', 'No change on record', 'No change of position on record.', ''),
 ('1914-11-16', 'The French relieve I Corps', 'The French begin relieving the British 1st and 2nd Divisions.', 'S44'),
 ('1914-11-17', 'Offensive called off', 'A last German attack south of the Menin road fails, and the Fourth Army gives up the offensive.', 'S40; S41'),
 ('1914-11-18', 'No change on record', 'No change of position on record.', ''),
 ('1914-11-19', 'No change on record', 'No change of position on record.', ''),
 ('1914-11-20', 'No change on record', 'No change of position on record.', ''),
 ('1914-11-21', 'No change on record', 'No change of position on record.', ''),
 ('1914-11-22', 'End of the battle', 'The French have taken over the salient from the British I Corps. The British official history ends the battle here.', 'S40'),
]
W = [
 ('1914-10-18', '1914-10-24', 'Week 1: the encounter battle', 'Both sides try to go round the other\'s open flank and meet head on. New German reserve corps drive in the Allied cavalry, take Roulers, Passchendaele and Becelaere, and stop the British advance on Menin. Haig\'s I Corps arrives and is halted north-east of Ypres; Langemarck holds. By the end of the week the French are taking over the north of the salient, and on the coast the Germans are over the Yser.', 'S40; S41; S42; S44; S45; S47'),
 ('1914-10-25', '1914-10-31', 'Week 2: Gheluvelt', 'The pressure moves to the Menin road. Kruiseik falls on the 26th and the cross-roads on the 29th. From the 30th the new German army group attacks south of the road: Zandvoorde, Hollebeke and then Gheluvelt fall, and Gheluvelt is retaken the same afternoon. Messines is stormed. On the coast the Belgian floods stop the Germans on the Yser.', 'S40; S41; S42; S43; S44'),
 ('1914-11-01', '1914-11-07', 'Week 3: the ridge lost, the line holds', 'Messines and Wytschaete are lost and the French take over the south. The British line round the east of Ypres holds, worn thin. The 7th Division is relieved, and the Germans take Klein Zillebeke but are checked at Zwarteleen.', 'S40; S41; S42; S43; S44'),
 ('1914-11-08', '1914-11-14', 'Week 4: Dixmude, St. Eloi and the Guard', 'The Germans bring the Guard into line for one more attack. Dixmude and St. Eloi fall on the 10th. On the 11th the Prussian Guard breaks through north of the Menin road to Nonne Bosschen and is thrown out. After that, no change of position is on record.', 'S40; S41; S42; S43'),
 ('1914-11-15', '1914-11-22', 'Last days: the offensive ends', 'The French relieve the British I Corps. A last German attack south of the Menin road fails on the 17th and the offensive is given up. The line that will form the Ypres salient for the rest of the war is set.', 'S40; S41; S44'),
]
wb = openpyxl.load_workbook(WB)
if 'Summaries' in wb.sheetnames: del wb['Summaries']
ws = wb.create_sheet('Summaries', index=wb.sheetnames.index('Events') + 1)
head = ['playback_id', 'kind', 'from', 'to', 'title', 'text', 'source_ids', 'how written']
ws.append(head)
for c in ws[1]: c.font = Font(bold=True)
how = 'From the workbook rows for the day (Positions: activity and place; Events), 19 Nov 2026. Says "no change on record" where the rows have none.'
for d, ti, tx, s in D: ws.append(['ypres', 'day', d, d, ti, tx, s, how])
for a, b, ti, tx, s in W: ws.append(['ypres', 'week', a, b, ti, tx, s, 'From the daily summaries of the week, 19 Nov 2026.'])
for col, w in zip('ABCDEFGH', (11, 7, 11, 11, 30, 90, 22, 40)): ws.column_dimensions[col].width = w
for row in ws.iter_rows(min_row=2):
    row[5].alignment = Alignment(wrap_text=True, vertical='top')
wb.save(WB); print('Summaries:', len(D), 'days,', len(W), 'weeks')
