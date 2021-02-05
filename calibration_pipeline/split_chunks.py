####################################################################################################

# split MS into chuncks
#######################

def split_chunks(MS_file, chunksize=100):

    """
    split an MS into channel  chuncks of size chunksize
    default chuck size is 100 channels
    """

    def get_lines(txt_file, expr):

        """
        get_lines(txt_file, expr)

        returns a list of lines of txt_file that match expr
        replaces grep -i expr txt_file
        """

        found_lines = []
        with open(txt_file, 'r') as infile:
            for line in infile:
                if not (line.find(expr) == -1):
                    found_lines.append(line)
        return found_lines


    casalog.post("*"*80)
    casalog.post("FUNCTION: SPLIT CHUNKS")
    casalog.post("*"*80)

    # get the number of channels in input MS
    nchan = int(get_lines(MS_file+'.listobs', 'XX  YY')[0].strip().split()[2])

    # break channels into chunks of length
    chans = np.arange(nchan)
    chunks = [chans[i:i+chunksize] for i in range(0, len(chans), chunksize)]

    vislist = []

    casalog.post("*"*80)
    casalog.post("splitting MS: "+MS_file)
    casalog.post("into these chunks: ")
    casalog.post("*"*80)

    for chan_chunk in chunks:

        spw = '0:'
        for chan in chan_chunk:
            spw += str(chan)
            spw += ';'
        spw = spw[:-1]

        outputvis = MS_file+'.chunk_'+str(chan_chunk[0])
        vislist.append(outputvis)

        casalog.post("*"*80)
        casalog.post("\t"+outputvis+"containing channel "+str(spw))
        casalog.post("*"*80)

        split(vis      = MS_file,
            outputvis  = outputvis,
            spw        = spw,
            datacolumn = 'data',
            width      = 1
        )

#    return vislist

####################################################################################################
