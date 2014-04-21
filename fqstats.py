#!/usr/bin/env python

import argparse
from collections import defaultdict
import sys
from Bio.SeqIO import parse
import matplotlib.pyplot as plt
from os.path import *
import numpy as np

def main( args ):
    plot_fqs( [(basename(fq),parse( fq, 'fastq' )) for fq in args.fastqs], 'out.png' )

def plot_fqs( iterable, out ):
    '''
        @param iterable - list of SeqRecord iterables(probably from Bio.SeqIO.parse)
        @param out - Output path of png
    '''
    # How many rows
    nrows = len( iterable )

    maxl = 0
    maxq = 0
    maxreads = 0
    maxreadsquals = 0
    stats = []
    # Compile all stats
    for fq,recs in iterable:
        s = fqstats(recs)
        if s[2] == 0 or s[3] == 0 or s[4] == 0 or s[5] == 0:
            nrows -= 1
            print 'Skipping {} because it has no sequences'.format(fq)
            continue
        # Empty seqs no graph
        stats.append( s )
        maxl = max( s[2], maxl )
        maxq = max( s[3], maxq )
        maxreads = max( s[4], maxreads )
        maxreadsquals = max( s[5], maxreadsquals )

    # Keep track of what subplot to graph on
    plotn = 1
    for i in range( len(stats) ):
        # The sequence records
        recs = list( iterable[i][1] )
        fqname = iterable[i][0]
        print fqname
        rlb, aqb, mlen, mqual, mreads, mquals = stats[i]
        # Plot the read length first on left
        print 'Plotting {}, 2, {}'.format(nrows, plotn)
        plt.subplot( nrows, 2, plotn )
        tname = fqname.replace('.fastq', '' )
        plot( plt.gca(), tname + ' ' + 'Read Length', rlb, maxl, maxreads )
        # Plot the avg qual on right
        plt.subplot( nrows, 2, plotn+1 )
        print 'Plotting {}, 2, {}'.format(nrows, plotn+1)
        plot( plt.gca(), tname + ' ' + 'Avg Qual', aqb, maxq, maxreadsquals )
        # 1,2 then 3,4 then 5,6 ....
        plotn += 2
    f = plt.gcf()
    f.set_size_inches( 16.0, 2.0*len(stats) )
    plt.savefig( out )

def fqstats( seqrecs ):
    '''
        Generates fqstats for a given iterator of SeqRecord objects
        @param seqrecs - Iterable of Bio.SeqRecord.SeqRecord's
        @returns tuple of
        - ReadLength bins
        - AvgQuality bins
        - Max read length
        - Max AvgQual
        - Max # readlens
        - Max # readquals
    '''
    stats = map( fqstat, seqrecs )

    # Pull out the columns of data
    rlb = map( lambda x: x[0], stats )
    aqb = map( lambda x: x[1], stats )
    # Compute maxes
    maxreadlen = max( rlb + [0] )
    maxaqual = max( aqb + [0] )
    # Bin values
    rlb, maxreads = bin_values( rlb )
    aqb, maxquals = bin_values( aqb )
    return (rlb, aqb, maxreadlen, maxaqual, maxreads, maxquals)

def fqstat( rec ):
    seqlen = len( rec.seq._data )
    aqual = read_avg_qual( rec )
    return (seqlen,aqual)

def read_avg_qual( rec ):
    '''
        Return the average quality of the qualities of given SeqRec object
    '''
    quals = rec._per_letter_annotations['phred_quality']
    if quals:
        avg = float(sum( quals )) / len( quals )
        return round( avg )
    else:
        return 0

def plot( ax, title, bins, max_x, max_y ):
    ax.set_title( title )
    vals = sorted( bins.items() )
    x = map( lambda x: x[0], vals )
    y = map( lambda x: x[1], vals )
    plt.xlim( -10, max_x )
    plt.ylim( 0, max_y )
    # Sanger reads only have 1 read so don't really show up unless we do this
    if len(x) == 1:
        x = [x[0]-1,x[0]]
        y = [y[0],y[0]]
    plt.fill_between( x, y )

def bin_values( valuelist ):
    '''
        Bins values in the given value list by counting the occurance of each
        item
    '''
    bins = defaultdict( int )
    maxv = 0
    for v in valuelist:
        bins[v] += 1
        maxv = max( maxv, bins[v] )
    return bins, maxv

def parse_args( args=sys.argv[1:] ):
    parser = argparse.ArgumentParser(
        description='Stats about fastq files'
    )

    parser.add_argument(
        'fastqs',
        nargs='+',
        help='Fastq files to get stats for'
    )

    return parser.parse_args( args )

if __name__ == '__main__':
    main( parse_args() )
