import time
import buptelecmon.animateprogress

ap = buptelecmon.animateprogress.AnimateProgress()

def test_bar_progress(capsys):
    ap.start_bar_progress('Bar Test Text')
    time.sleep(5.1)
    ap.stop_progress()
    outerr = capsys.readouterr()
    if isinstance(outerr, tuple):
        out = outerr[0]
    else:
        out = outerr.out
    assert out == 'Bar Test Text...........\n'

def test_rotate_progress(capsys):
    ap.start_rotated_progress('Rotated Test Text')
    time.sleep(2.1)
    ap.stop_progress()
    outerr = capsys.readouterr()
    if isinstance(outerr, tuple):
        out = outerr[0]
    else:
        out = outerr.out
    assert out == 'Rotated Test Text \b-\b\\\b|\b/\b-\n'
