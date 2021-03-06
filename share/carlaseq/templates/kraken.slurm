{slurmheader}

###
# Author:      Andrew Robinson
# Date:        2014-12-08
# Description: Uses kraken to classify contaminant sequences.
###

# Command used to generate this file:
# {CMD}

FILES="{files}"

# load modules
module load kraken-gcc/{krakenversion} limsradseq

carlaseq_log Starting $0

# process each raw sequence file
MD5=""
for SRCFILENAME in ${{FILES}}; do
    echo "Running: $SRCFILENAME at: " `date`
    OUTFILE=$(basename $SRCFILENAME);
    OUTFILE=${{OUTFILE%%.*}}

    # run kraken
    CMD="kraken-lims --preload --unclassified-out ${{OUTFILE}}_unclassified.fastq \
        --classified-out ${{OUTFILE}}_classified.fastq \
        --output ${{OUTFILE}}_output.tsv --fastq-input $SRCFILENAME"
    echo $CMD
    $CMD;

    # compute md5 hash
    CMD="md5sum ${{OUTFILE}}_classified.fastq"
    echo $CMD
    MD5="$MD5\\n`$CMD`"
    CMD="md5sum ${{OUTFILE}}_unclassified.fastq"
    echo $CMD
    MD5="$MD5\\n`$CMD`"
done

# print details of output files (provenance)
echo -e "\\nDirectory Contents:"
ls -l
echo ""
echo -e $MD5
echo ""

carlaseq_log Finished $0

