import pandas as pd
import numpy as np
import argparse
import sys

from .cmseq import CMSEQ_DEFAULTS
from .cmseq import BamFile

def polymut_from_file():
	parser = argparse.ArgumentParser(description="Reports the polymorpgic rate of each reference (polymorphic bases / total bases). Focuses only on covered regions (i.e. depth >= 1)")
	parser.add_argument('BAMFILE', help='The file on which to operate')
	parser.add_argument('-c','--contig', help='Focus on a subset of references in the BAM file. Can be a list of references separated by commas or a FASTA file (the IDs are used to subset)', metavar="REFERENCE ID" ,default=None)
	parser.add_argument('-f', help='If set unmapped (FUNMAP), secondary (FSECONDARY), qc-fail (FQCFAIL) and duplicate (FDUP) are excluded. If unset ALL reads are considered (bedtools genomecov style). Default: unset',action='store_true')
	parser.add_argument('--sortindex', help='Sort and index the file',action='store_true')
	parser.add_argument('--minlen', help='Minimum Reference Length for a reference to be considered. Default: '+str(CMSEQ_DEFAULTS.minlen),default=CMSEQ_DEFAULTS.minlen, type=int)
	parser.add_argument('--minqual', help='Minimum base quality. Bases with quality score lower than this will be discarded. This is performed BEFORE --mincov. Default: 30', type=int, default=CMSEQ_DEFAULTS.minqual)
	parser.add_argument('--mincov', help='Minimum position coverage to perform the polymorphism calculation. Position with a lower depth of coverage will be discarded (i.e. considered as zero-coverage positions). This is calculated AFTER --minqual. Default:'+str(CMSEQ_DEFAULTS.mincov), type=int, default=CMSEQ_DEFAULTS.mincov)
	parser.add_argument('--dominant_frq_thrsh', help='Cutoff for degree of `allele dominance` for a position to be considered polymorphic. Default: '+str(CMSEQ_DEFAULTS.poly_dominant_frq_thrsh), type=float, default=CMSEQ_DEFAULTS.poly_dominant_frq_thrsh)
	parser.add_argument('--gff_file', help="GFF file used to extract protein-coding genes", default = None)
	args = parser.parse_args()

	import pandas as pd

	outputDicts=[]

	si = True if args.sortindex else False
	mode = 'all' if args.f else 'nofilter'

	bf = BamFile(args.BAMFILE,sort=si,index=si,stepper=mode,minlen=args.minlen,filtRefGenomes=args.contig)

	if (args.gff_file):
		bf.parse_gff(args.gff_file)

	for i in bf.get_contigs_obj():
		dominanceArray, mutationStats = i.easy_polymorphism_rate(minqual=args.minqual,mincov=args.mincov,dominant_frq_thrsh=args.dominant_frq_thrsh)
		outputDicts.append({'Ref':i.name, 'DN':mutationStats['DN'],'DS':mutationStats['DS'],'D?':mutationStats['D?'], "consid_pos":len([x for x in dominanceArray if not np.isnan(x)])})
	out_df = pd.DataFrame.from_dict(outputDicts).set_index('Ref')
	print(float(np.sum(out_df["DN"])), float(np.sum(out_df["DS"])), float(sum(out_df["consid_pos"])))

if __name__ == "__main__":
	polymut_from_file()
