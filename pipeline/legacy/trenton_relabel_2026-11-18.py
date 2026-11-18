"""18 Nov 2026: the battle is called the First Battle of Trenton (Morgan)."""
import openpyxl
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(WB)
ch = {('Battles', 'D5'): ('Battle of Trenton', 'First Battle of Trenton'),
      ('Playbacks', 'E3'): ('Trenton, 26 December 1776', 'First Battle of Trenton, 26 December 1776'),
      ('Playback settings', 'C63'): ('Trenton 1776 Playback', 'First Battle of Trenton (1776) Playback'),
      ('Playback settings', 'C191'): ('Battle of Trenton', 'First Battle of Trenton')}
for (s, cell), (old, new) in ch.items():
    assert wb[s][cell].value == old, (s, cell, wb[s][cell].value); wb[s][cell].value = new
wb.save(WB); print('relabelled')
