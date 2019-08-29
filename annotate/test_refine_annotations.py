import pytest
import pandas as pd
import refine_annotations as ra
from intervaltree import Interval, IntervalTree

###############################################################
# dummy arguments
###############################################################
args = type('argparse.Namespace', (object,),
            {'minClip': 20, 'minGap': 7})()
ra.set_globals(args)

###############################################################
# test data
###############################################################

# make reference -- chrom1
# these data could represent exons or genes
ex_trees = {}
ref_tree = IntervalTree()
coords = [(100, 200),
          (300, 400)]
for s,e in coords:
    ref_tree.addi(s, e)
ex_trees['chr1'] = ref_tree

# make reference -- chrom2
ref_tree = IntervalTree()
coords = [(500, 600),
          (800, 900)]
for s,e in coords:
    ref_tree.addi(s, e)
ex_trees['chr2']= ref_tree

@pytest.mark.parametrize('coord,expected', [((150, 160), True),
                                            ((90, 101), False),
                                            ((198, 205), False),
                                            ((193, 200), True),
                                            ((100, 107), True)])
def test_check_overlap_del(coord, expected):
    s, e = coord
    assert ra.check_overlap(ex_trees, 'chr1', s, e, size = args.minGap) == expected

@pytest.mark.parametrize('coord,expected', [((150, 160), True),
                                            ((90, 150), False),
                                            ((150, 250), False),
                                            ((301, 399), True),
                                            ((150, 350), False),
                                            ((50, 60), False)])
def test_overlaps_same_exon(coord, expected):
    s, e = coord
    pos1 = 'chr1:%s(+)' % s
    pos2 = 'chr1:%s(-)' % e
    sv = pd.Series({'pos1': pos1, 'pos2': pos2})
    assert ra.overlaps_same_exon(sv, ex_trees) == expected

@pytest.mark.parametrize('coord,expected', [(('chr1:100(+)', 'chr1:200(+)'), True),
                                            (('chr1:101(+)', 'chr2:400(+)'), True),
                                            (('chr1:450(+)', 'chr2:501(+)'), True),
                                            (('chr1:550(+)', 'chr1:650(+)'), False),
                                            (('chr2:550(+)', 'chr2:650(+)'), True),
                                            (('chr2:150(+)', 'chr2:250(+)'), False)])
def test_overlaps_gene(coord, expected):
    row = {'pos1': coord[0], 'pos2': coord[1]}
    assert ra.overlaps_gene(row, ex_trees) == expected
