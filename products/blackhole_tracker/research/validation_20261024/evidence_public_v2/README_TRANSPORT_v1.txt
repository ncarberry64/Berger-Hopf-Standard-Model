BHSM CURRENT-KERNEL CALIBRATION: COMPLETE SAVED-EVIDENCE TRANSPORT

This is content transport, not a new calibration run or scientific approval.
The producer processed4608 synthetic datasets/4736 fits. Its retained outcomes
include3 short-cadence calibration warnings and negative controls that often
pass a scalar chi-square screen. No BH classifier FPR/FNR, native known-BH
recovery or publication-HOLD clearance follows. Source identities, missing
quantities, all cases and independent audit/diagnosis records are retained.

TWO DISTINCT SCOPES

LOCAL archive: all campaign files, full102-member frozen source/original/
prepared-cadence snapshot, original freeze and review evidence. It contains
the2 actual raw OGLE cadence files and2 prepared-parent documents carrying
original native brightness. It is a local complete audit copy, not a claim
of permission to redistribute native OGLE files publicly.

PUBLIC archive: all synthetic generated inputs/outcomes, top-level summaries,
plots, source code, complete case accounting, original-source hashes and
independent audit evidence. Actual raw OGLE bytes and prepared-parent native
brightness docs are explicitly omitted. There are4 distinct native entities
but6 omitted stored copies because the two prepared parents also appear in
the preparation review folder. The public manifest lists every omitted
member, original path, byte count and SHA256. PUBLIC is NOT original-native-
complete and must never be described as such. Raw times/errors/row identities
retained in the synthetic studies keep their source attribution; no new
third-party permission is granted by this bundle. Author/source licenses
and source-provider terms continue to apply.

NORMALIZATION AND EXACTNESS

Every generated/outcome .json.gz is transported as its EXACT decompressed
JSON byte payload; it is not reserialized or numerically normalized. All
other included files are exact bytes. One solid tar.xz dictionary compresses
repeated fields and nearby input/outcome copies. The external manifest and
its identical archived copy bind original gzip SHA/size, payload SHA/size,
restored path, original source path and transport rule for every member.
No failed/unresolved case is dropped to achieve an archive-size target.

Hashes establish byte consistency, not independent source authenticity or
scientific validity. Obtain the manifest SHA from the reviewed release record.
The manifest does not hash itself; the external build receipt hashes both
the manifest and archive. Producer zlib was not separately frozen before the
study. Transport/runtime receipts record the actual reconstruction runtime;
original gzip identity is claimed only when EVERY original hash matches.

VERIFY WITHOUT EXECUTING ARCHIVED SCIENTIFIC CODE

Use the external restore_verify_calibration_v1.py with a manifest/archive
pair and the reviewed manifest SHA. All output receipt paths must be new.

  python restore_verify_calibration_v1.py --archive ARCHIVE.tar.xz
    --manifest TRANSPORT_MANIFEST_LOCAL_v1.json --manifest-sha256 SHA
    --mode verify-payloads --receipt NEW-payload-receipt.json

The same operation works with the PUBLIC pair. This mode verifies every
included normalized payload across Python runtimes without assuming identical
gzip compressors. It extracts no files and executes no archived helper/model.
It DOES NOT establish original gzip byte identity.

To restore all included originals under the demonstrated3.14/zlib runtime:

  python restore_verify_calibration_v1.py --archive ARCHIVE.tar.xz
    --manifest MANIFEST.json --manifest-sha256 SHA --mode restore-originals
    --output NEW-directory --receipt NEW-restoration-receipt.json

Normalized entries are recompressed using gzip.compress(level5,mtime0), and
every original SHA/size must match before its file is written. Other files
are restored byte-exact. A mismatch is explicit GZIP_RUNTIME_BYTE_IDENTITY_
UNRESOLVED; partial output/events are preserved and no existing file is
overwritten. Such a runtime may still verify normalized payloads. Restoring
the PUBLIC archive restores only its explicitly included subset; omitted
native files are not synthesized.

BOUNDED REACQUISITION OF OMITTED NATIVE PARENTS

The public source snapshot retains the exact download_manifest.json and
pilot_selection.json, acquisition URLs and raw SHA/size. Reacquire only the
two named cadence files from their provider links into a separate data root;
retain provider attribution/terms and do not substitute changed bytes. If a
provider response differs, report unavailable/new data version rather than
silently adopting it. No network fetch is performed by the transport helper.

To reconstruct the prepared parents, use the exact preserved product schema/
parser and calibrate_rc7.py prepare command with those original metadata and
verified raw files, in a new external directory. This preparation fits no
brightness. Compare CADENCE_PARENT_0/1 JSON hashes to the source-snapshot map
before treating them as the historical parents. Existing interpreter/source
paths and runtime bindings are historical provenance: a relocated rerun needs
an explicit new local preparation/admission record, not an edited old freeze.
No scientific study is automatically rerun by extraction or verification.

The current local complete archive and original files remain preserved even
when a public subset is published. Publication of any raw third-party data
requires its own applicable rights determination; this transport grants none.
