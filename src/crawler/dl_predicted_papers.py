import argparse
import os
import requests
import time


def _get_oa_body(pmc_id, outfolder):
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=%s' % pmc_id
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        xml_target = outfolder + '/' + pmc_id + '.xml'
        if not os.path.isfile(xml_target):
            with open(xml_target, 'w') as f:
                f.write(response.content)
        return True
    else:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filter-type', help='Filter used for prediction',
            choices=['basic', 'weak', 'strong'])
    parser.add_argument('--download-folder', help='Path to target folder')
    parser.add_argument('--wait', help='Wait time in between server calls',
            type=int, default=1)
    args = parser.parse_args()

    predicted_papers_file = '../../data/db/predicted/' + args.filter_type
    with open(predicted_papers_file) as f:
        lines = f.readlines()
        for pmc_id in lines:
            _get_oa_body(pmc_id, args.download_folder)
            time.sleep(args.wait)


if __name__ == "__main__":
    main()
