"""Verify a held local RC7 author-review packet; never upload or attest for an author."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import zipfile

PAPER = Path(__file__).resolve().parents[2]
REPOSITORY = 'https://github.com/ncarberry64/Berger-Hopf-Standard-Model'
HERE = PAPER/'submission/rc7'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_hold(metadata):
    """A local packaging success cannot turn into scientific publication approval."""
    if metadata.get('manual_submission_only') is not True or metadata.get('ready_for_submission') is not False:
        raise ValueError('RC7 preparation is manual only and ready_for_submission must remain false')
    hold = metadata.get('publication_hold')
    required = {
        'status': 'HOLD',
        'primary_investigation_target': 'Gaia18ajz',
        'primary_candidate_previously_published': True,
        'new_engine_BH_interpretation_established': False,
        'native_candidate_analysis_adequate': False,
        'known_black_hole_recovery_validated': False,
        'photometric_uncertainty_calibration_failures': 3,
        'normalized_student_native_recovery_status': 'NUMERICALLY_UNRESOLVED',
    }
    if not isinstance(hold, dict) or any(type(hold.get(k)) is not type(v) or hold.get(k) != v for k,v in required.items()):
        raise ValueError('Explicit Gaia18ajz prior-publication and unresolved candidate/recovery HOLD facts are required')
    return hold


def prepare(output):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError('Use a fresh external output directory; prior packets are never overwritten')
    if output.is_relative_to(PAPER.resolve()):
        raise ValueError('Keep generated author-review packets outside the manuscript source tree')
    metadata_path = HERE/'submission_metadata.json'
    cover_path = HERE/'cover_letter_draft.md'
    # These final files must be supplied only after final code/PDF/validation pins exist.
    metadata = json.loads(metadata_path.read_text(encoding='utf8'))
    hold = require_hold(metadata)
    if metadata.get('all_final_bindings_supplied') is not True:
        raise ValueError('Final PDF, visual QA and immutable paper/source pins are explicitly pending; do not prepare this draft')
    if metadata.get('status') != 'PREPARED_FOR_AUTHOR_REVIEW_PUBLICATION_HOLD':
        raise ValueError('Final metadata must explicitly retain the prepared author-review publication HOLD status')
    for key in ('reviewed_paper_source_commit', 'formal_source_snapshot_commit'):
        if re.fullmatch(r'[0-9a-f]{40}', metadata.get('final_source_bindings', {}).get(key) or '') is None:
            raise ValueError('Final immutable paper/source commit binding is missing: '+key)
    if metadata.get('submission_actions_performed') != []:
        raise ValueError('This manual preparation does not assert a submission action')
    source_path = PAPER/'manuscript/main.tex'
    source = source_path.read_text(encoding='utf8')
    match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', source, re.S)
    if match is None:
        raise ValueError('The manuscript abstract is missing')
    abstract = ' '.join(match.group(1).replace(r'\,', ',').replace(r'\%', '%').replace('--', '\u2013').split())
    if abstract != metadata['abstract']:
        raise ValueError('Submission abstract differs from the manuscript')
    if digest(source_path) != metadata.get('abstract_input_source_sha256'):
        raise ValueError('Final manuscript source differs from metadata source binding')
    if len(abstract.split()) > 200:
        raise ValueError('Submission abstract exceeds 200 words')
    formal = metadata['formal_repository']
    commit = formal.get('code_commit', '')
    if (formal.get('url') != REPOSITORY or re.fullmatch(r'[0-9a-f]{40}', commit) is None
            or commit not in source
            or formal.get('code_url') != REPOSITORY+'/tree/'+commit+'/products/blackhole_tracker'
            or formal.get('code_version') != 'bhsm-blackhole-tracker 0.2.0rc7'):
        raise ValueError('Final canonical BHSM RC7 repository/code citation differs')
    validation = metadata.get('local_release_validation')
    if (not isinstance(validation, dict) or validation.get('product_version') != '0.2.0rc7'
            or validation.get('scientific_acceptance') != 'NOT_ESTABLISHED'
            or re.fullmatch(r'[0-9a-f]{64}', validation.get('wheel_sha256', '')) is None):
        raise ValueError('Final RC7 wheel/validation metadata with unresolved scientific acceptance is required')
    pdf = PAPER/'manuscript/main.pdf'
    if not pdf.read_bytes().startswith(b'%PDF-'):
        raise ValueError('Compiled manuscript PDF is missing or invalid')
    manuscript = metadata['manuscript']
    if digest(pdf) != manuscript['reviewed_pdf_sha256']:
        raise ValueError('PDF differs from the visually reviewed metadata binding')
    if type(manuscript.get('pages')) is not int or manuscript['pages'] <= 0:
        raise ValueError('Final reviewed PDF page count is required in metadata')
    if (manuscript.get('independent_pdf_qa_status') != 'PASS'
            or re.fullmatch(r'[0-9a-f]{64}', manuscript.get('independent_pdf_qa_sha256') or '') is None
            or pdf.stat().st_size != manuscript.get('reviewed_pdf_bytes')):
        raise ValueError('Exact final visually reviewed PDF/QA binding is required')
    bbl = PAPER/'manuscript/main.bbl'
    if (re.fullmatch(r'[0-9a-f]{64}', manuscript.get('matching_bbl_sha256') or '') is None
            or digest(bbl) != manuscript['matching_bbl_sha256']
            or bbl.stat().st_size != manuscript.get('matching_bbl_bytes')):
        raise ValueError('The matching compiled bibliography binding is required')
    cover = cover_path.read_text(encoding='utf8').casefold()
    if any(text not in cover for text in ('gaia18ajz', 'previously published', 'publication hold')):
        raise ValueError('The held cover-letter draft must retain the candidate history and publication hold')
    members = sorted(path for folder in ['manuscript', 'figures']
                     for path in (PAPER/folder).rglob('*')
                     if path.is_file() and path.suffix.lower() in {'.tex', '.bib', '.bbl', '.pdf', '.png', '.jpg', '.jpeg', '.eps'}
                     and path != pdf)
    joint_figure = PAPER/'joint_known_system_20261022/joint_noise_diagnostics.png'
    if not joint_figure.is_file():
        raise ValueError('The joint manuscript diagnostic figure is missing')
    members = sorted(set(members + [joint_figure]))
    if not members or source_path not in members:
        raise ValueError('Complete LaTeX sources are required')
    if sum(path.stat().st_size for path in members)+pdf.stat().st_size > 120_000_000:
        raise ValueError('Journal files exceed 120 MB before compression')
    inputs = sorted(set(members + [pdf, metadata_path, cover_path, Path(__file__)]))
    before = {str(path):digest(path) for path in inputs}
    # Every prerequisite above is read-only. Exclusive creation owns this new packet.
    output.mkdir(parents=True, exist_ok=False)
    try:
        archive_path = output/'Galaxies_Manuscript_Source.zip'
        with zipfile.ZipFile(archive_path, 'x', zipfile.ZIP_DEFLATED) as archive:
            for path in members:
                info = zipfile.ZipInfo(path.relative_to(PAPER).as_posix(), date_time=(1980,1,1,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
        with zipfile.ZipFile(archive_path) as archive:
            if archive.testzip() is not None or set(archive.namelist()) != {p.relative_to(PAPER).as_posix() for p in members}:
                raise ValueError('LaTeX archive member/CRC verification failed')
            for path in members:
                if archive.read(path.relative_to(PAPER).as_posix()) != path.read_bytes():
                    raise ValueError('LaTeX archive member differs from reviewed source')
        outputs = [archive_path]
        for path, name in [(pdf, 'BHSM_Blackhole_Tracker_Manuscript.pdf'),
                           (metadata_path, 'submission_metadata.json'),
                           (cover_path, 'cover_letter_draft.md')]:
            target = output/name
            with target.open('xb') as stream:
                stream.write(path.read_bytes())
            if target.read_bytes() != path.read_bytes():
                raise ValueError('Author-review copy differs from its source')
            outputs.append(target)
        if any(digest(path) != before[str(path)] for path in inputs):
            raise ValueError('Reviewed source changed during preparation')
        receipt = {'status':'PREPARED_FOR_AUTHOR_REVIEW_PUBLICATION_HOLD', 'uploaded':False,
                   'ready_for_submission':False, 'manual_submission_only':True,
                   'publication_hold':hold, 'formal_repository':formal,
                   'abstract_words':len(abstract.split()), 'reviewed_pdf_pages_from_metadata':manuscript['pages'],
                   'page_count_qualification':'Hash-bound reviewed metadata; this stdlib script does not render or independently count PDF pages.',
                   'local_release_validation_from_metadata':validation,
                   'source_members':{path.relative_to(PAPER).as_posix():digest(path) for path in members},
                   'files':{path.name:{'sha256':digest(path),'bytes':path.stat().st_size} for path in outputs},
                   'source_bytes_unchanged':True, 'preparation_source_sha256':digest(Path(__file__)),
                   'submission_actions_performed':[],
                   'author_confirmation_needed_before_final_submission':metadata['author_confirmation_needed_before_final_submission']}
        with (output/'submission_preflight.json').open('x',encoding='utf8',newline='\n') as stream:
            json.dump(receipt,stream,indent=2,allow_nan=False);stream.write('\n')
        return receipt
    except BaseException as error:
        with (output/'submission_preflight_failure.json').open('x',encoding='utf8',newline='\n') as stream:
            json.dump({'status':'FAILED_RETAINED_FOR_REVIEW','uploaded':False,'ready_for_submission':False,
                       'publication_hold':'HOLD','error_type':type(error).__name__,'error':str(error)},stream,indent=2);stream.write('\n')
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    args = parser.parse_args()
    result = prepare(args.output)
    print(json.dumps({'status':result['status'],'uploaded':False,'ready_for_submission':False,
                      'abstract_words':result['abstract_words'],'source_members':len(result['source_members'])},indent=2))
