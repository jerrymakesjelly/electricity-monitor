import time
import buptelecmon.animateprogress

ap = buptelecmon.animateprogress.AnimateProgress()

def test_bar_progress(capsys):
    ap.start_bar_progress('Bar Test Text')
    time.sleep(5.1)
    ap.stop_progress()
    assert capsys.readouterr().out == 'Bar Test Text...........\n'

def test_rotate_progress(capsys):
    ap.start_rotated_progress('Rotated Test Text')
    time.sleep(2.1)
    ap.stop_progress()
    assert capsys.readouterr().out == 'Rotated Test Text \b-\b\\\b|\b/\b-\n'
