import argparse
from contextlib import closing
import numpy as np
import os
import requests
import time
import urllib


def _get_oa_body(pubmed_id, pmc_id, outfolder):
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=%s' % pmc_id
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        xml_target = outfolder + '/' + str(pubmed_id) + '.xml'
        if not os.path.isfile(xml_target):
            with open(xml_target, 'w') as f:
                f.write(response.content)
        return True
    else:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-files', help='Number of papers to download',
            type=int)
    parser.add_argument('--download-folder', help='Path to target folder')
    parser.add_argument('--wait', help='Wait time in between server calls',
            type=int, default=1)
    args = parser.parse_args()

    url = 'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.txt'
    with closing(urllib.urlopen(url)) as f:
        lines = f.readlines()[1:]
        n_lines = len(lines)
        order = np.random.permutation(n_lines)
        for i in order[:args.num_files]:
            fields = lines[i].strip().split('\t')
            if len(fields) < 4: continue
            pmid = fields[3][5:]
            pmc = fields[2]
            if pmid == '' or pmc == '': continue
            _get_oa_body(int(pmid), pmc, args.download_folder)
            time.sleep(args.wait)


if __name__ == "__main__":
    main()
