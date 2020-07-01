from pprint import pprint

from project.music_gen.core import *
from project.music_gen.data_types import *
from pprint import pprint as p

t_len = 3

hit_quarter = note_replicator(Tempo.QUARTER, Abs_note.HI_HAT_CLOSE,
                              list(Quarters))

snares = note_replicator(Tempo.QUARTER, Abs_note.SNARE,
                         [Quarters.TWO, Quarters.FOUR])

basses = note_replicator(Tempo.QUARTER, Abs_note.BASS_DRUM,
                         [Quarters.ONE, Quarters.THREE])

std_groove = hit_quarter + snares + basses

bass0 = note_generator(Note(Tempo.QUARTER, Abs_note.BASS_DRUM, Quarters.ONE),
                       t_len)
bass2 = note_generator(
    Note(Tempo.EIGHTH, Abs_note.BASS_DRUM, Quarters.THREE, 1), t_len) // (3,[0,1])

basss = bass0 + bass2

classic =  (hit_quarter*3)+ (snares*3) + basss


test_g = hit_quarter[1] | classic * 2 | ((hit_quarter + basss) * 2)[3]

test = classic | std_groove * 2 | test_g

test3 = test * 2

test4 = test[2]

# def quartes_gen(tempo: Tempo):
#     for x in range(tempo.value):
#         yield (x, Quarters(int(x / (tempo.value / 4)) + 1))

# def measure_generator(max_note: int, note: Note):
#     while True:
#         yield [[
#             note.val if idx == note.note.value else 0
#             for idx in range(max_note)
#         ] for _ in range(note.tempo.value)]

# def pippo():
#     a = mona()
#     b = gna()
#     for i, j in zip(a, b):
#         yield i + j + "last"

# def mona():
#     a = test()
#     for i in a:
#         yield i + "normal"

# def gna():
#     a = test()
#     for i in a:
#         newa = test()
#         for i in newa:
#             yield i + "nested"

# def test():
#     for i in (1, 2, 3):
#         yield str(i) + "base"

len_ = 1

ride = note_generator(Note(Tempo.QUARTER, Abs_note.RIDE, Quarters.FOUR), len_)

bass = note_generator(Note(Tempo.QUARTER, Abs_note.BASS_DRUM, Quarters.ONE),
                      len_)

charl = note_replicator(Tempo.EIGHTH, Abs_note.HI_HAT_CLOSE,
                        [Quarters.ONE, Quarters.THREE])

ttest = bass + charl + ride

n0 = note_replicator(Tempo.QUARTER, Abs_note.MID_TOM, [Quarters.TWO])
n1 = note_replicator(Tempo.QUARTER, Abs_note.CRASH, [Quarters.TWO])
n2 = note_replicator(Tempo.QUARTER, Abs_note.HI_HAT_CLOSE,
                     [Quarters.ONE, Quarters.THREE])

add = n0 + n1 + n2

n3 = note_replicator(Tempo.EIGHTH, Abs_note.SNARE, [Quarters.THREE])
n4 = note_replicator(Tempo.EIGHTH, Abs_note.HIG_TOM, [Quarters.FOUR]) * 2
n5 = note_replicator(Tempo.QUARTER, Abs_note.HI_HAT_OPEN, [Quarters.ONE]) * 2

add1 = (n0 + n3 + n4) | (n5 + n1 + n2)

test_patterns = [ttest, add, add1]

# pprint(list((add1)()))
