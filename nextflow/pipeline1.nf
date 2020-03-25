#!/usr/local/bin/env nextflow

// Script parameters
params.query = "/some/data/sample.fa"
params.db = "/some/path/pdb"

db = file(params.db)
query_ch = Channel.fromPath(params.query)

process blastSearch {
    input:
    file query from query_ch

    output:
    file "top_hits.txt" into top_hits_ch

    """
    blastp -db $db -query $query -outfmt 6 > blast_result
    cat blast_result | head -n 10 | cut -f 2 > top_hits.txt
    """
}

process extractTopHits {
    input:
    file top_hits from top_hits_ch

    output:
    file "sequences.txt" into sequences_ch

    """
    blastdbcmd -db $db -entry_batch $top_hits > sequences.txt
    """
}
