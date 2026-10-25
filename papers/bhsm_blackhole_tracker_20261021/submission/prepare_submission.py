"""Prepare and verify the local journal files; never uploads or attests for an author."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import zipfile

PAPER = Path(__file__).resolve().parents[1]
REPOSITORY = 'https://github.com/ncarberry64/Berger-Hopf-Standard-Model'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(output):
    output.mkdir(parents=True, exist_ok=True)
    metadata_path = PAPER/'submission/submission_metadata.json'
    metadata = json.loads(metadata_path.read_text(encoding='utf8'))
    source = (PAPER/'manuscript/main.tex').read_text(encoding='utf8')
    abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', source, re.S).group(1)
    abstract = ' '.join(abstract.replace(r'\%', '%').replace('--', '\u2013').split())
    if abstract != metadata['abstract']:
        raise ValueError('Submission abstract differs from the manuscript')
    if len(abstract.split()) > 200:
        raise ValueError('Submission abstract exceeds200 words')
    formal = metadata['formal_repository']
    if formal['url'] != REPOSITORY or formal['code_commit'] not in source:
        raise ValueError('Canonical BHSM repository/code citation differs')
    pdf = PAPER/'manuscript/main.pdf'
    if not pdf.read_bytes().startswith(b'%PDF-'):
        raise ValueError('Compiled manuscript PDF is missing or invalid')
    if digest(pdf) != metadata['manuscript']['reviewed_pdf_sha256']:
        raise ValueError('PDF differs from the visually reviewed metadata binding')
    members = sorted(path for folder in ['manuscript', 'figures']
                     for path in (PAPER/folder).rglob('*')
                     if path.is_file() and path.suffix.lower() in {'.tex', '.bib', '.bbl', '.pdf', '.png', '.jpg', '.jpeg', '.eps'}
                     and path != pdf)
    # The separate joint audit owns this byte-pinned figure; keep its relative
    # path so the focused journal archive compiles without the reviewer tree.
    joint_figure = PAPER/'joint_known_system_20261022/joint_noise_diagnostics.png'
    if not joint_figure.is_file():
        raise ValueError('The joint manuscript diagnostic figure is missing')
    members = sorted(set(members + [joint_figure]))
    if not members or PAPER/'manuscript/main.tex' not in members:
        raise ValueError('Complete LaTeX sources are required')
    if sum(path.stat().st_size for path in members)+pdf.stat().st_size > 120_000_000:
        raise ValueError('Journal files exceed120MB before compression')
    archive_path = output/'Galaxies_Manuscript_Source.zip'
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in members:
            info = zipfile.ZipInfo(path.relative_to(PAPER).as_posix(), date_time=(1980,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            raise ValueError('LaTeX archive CRC verification failed')
        for path in members:
            if archive.read(path.relative_to(PAPER).as_posix()) != path.read_bytes():
                raise ValueError('LaTeX archive member differs from reviewed source')
    outputs = [archive_path]
    for path, name in [(pdf, 'BHSM_Blackhole_Tracker_Manuscript.pdf'),
                       (metadata_path, 'submission_metadata.json'),
                       (PAPER/'submission/cover_letter_draft.md', 'cover_letter_draft.md')]:
        target = output/name
        if path.resolve() != target.resolve():
            shutil.copy2(path, target)
        outputs.append(target)
    receipt = {'status':'PREPARED_AND_VERIFIED_FOR_AUTHOR_REVIEW', 'uploaded':False,
               'ready_for_submission':False, 'formal_repository':formal,
               'abstract_words':len(abstract.split()),
               'source_members':{path.relative_to(PAPER).as_posix():digest(path) for path in members},
               'files':{path.name:{'sha256':digest(path),'bytes':path.stat().st_size} for path in outputs},
               'author_confirmation_needed_before_final_submission':metadata['author_confirmation_needed_before_final_submission']}
    (output/'submission_preflight.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    args = parser.parse_args()
    result = prepare(args.output.resolve())
    print(json.dumps({'status':result['status'],'uploaded':False,'abstract_words':result['abstract_words'],
                      'source_members':len(result['source_members'])},indent=2))
