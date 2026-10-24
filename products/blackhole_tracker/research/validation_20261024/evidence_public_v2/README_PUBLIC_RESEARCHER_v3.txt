Public researcher delivery v2

The original PUBLIC tar.xz is119,420,524bytes: above100MB, with every synthetic
case retained. Three numbered parts (<=40MiB each) preserve that archive exactly.
Only those parts/small helpers belong in ordinary Git; neither the assembled
archive nor this119MB ZIP is suitable as a normal Git blob. LOCAL complete
archive remains external and contains the native observations; never publish it
without a separately established source-specific right.

The public content includes all4,608 synthetic inputs/4,736 outcomes, failures,
plots, original source pins and selected study sources. It omits six copies of
four native entities, explicitly listed in TRANSPORT_MANIFEST_PUBLIC_v1.json.
Omitted files are two OGLE originals and two native-brightness prepared parents.
No missing synthetic cases, native substitutions or scientific reruns occur.

Verify and join (standard Python library only; no extraction/code execution):
  python -I -B join_public_evidence_v1.py --manifest PUBLIC_PARTS_MANIFEST_v1.json --manifest-sha256 PARTS_MANIFEST_SHA --receipt NEW_JOIN_RECEIPT.json --output NEW_PUBLIC.tar.xz
Read PARTS_MANIFEST_SHA from PUBLIC_DELIVERY_MANIFEST_v2.json or the pinned release
index. Omitting --output verifies the same assembled content without writing it.
The assembled archive must be SHA256:
  91f501317821e937d22d52fbea20130995911ed2f1562409b073fc900fa7710e

Verify every normalized payload on Python3.11 or3.14, extracting nothing:
  python -I -B restore_verify_calibration_v1.py --archive NEW_PUBLIC.tar.xz --manifest TRANSPORT_MANIFEST_PUBLIC_v1.json --manifest-sha256 1244b6865dd553b98aff5de78829fc2f176b00ff2f8e8c01f3c0e3dd84dd176d --mode verify-payloads --receipt NEW_VERIFY_RECEIPT.json

Restore included originals only (NEW output root;~350MB original bytes):
  python -I -B restore_verify_calibration_v1.py --archive NEW_PUBLIC.tar.xz --manifest TRANSPORT_MANIFEST_PUBLIC_v1.json --manifest-sha256 1244b6865dd553b98aff5de78829fc2f176b00ff2f8e8c01f3c0e3dd84dd176d --mode restore-originals --output NEW_RESTORED --receipt NEW_RESTORE_RECEIPT.json
The producer used gzip level5/mtime0. Exact original gzip reconstruction has been
demonstrated separately on Python3.14.3/zlib1.3.1.zlib-ng; other compressors may
produce different bytes and must fail exact-byte restoration conservatively.
Normalized payload verification is portable and does not assert gzip identity.
Restoration never runs archived code. No source authenticity/validity follows
from self-consistent hashes alone.

To obtain the two native cadence files and prepare a fresh local execution
freeze from a source distribution, see cadence_preparation_kit_v2/. Default
helper operation performs no network. Explicit download is bounded/hash-gated,
uses only the original provider, and writes only a NEW external data root.
The exact selection/download metadata and source URLs/hash/path mapping are
included. No original absolute C: paths or private attachment are needed.

This is scientific evidence transport, not calibration approval. The completed
study has three gross nominal95% calibration flags in P1 PSPL (tE/u0/profile
truth membership). Scalar photometric nonrejection is not a BH classifier; BH
false-positive/negative rates and known-native recovery remain unavailable.
BHSM interpretation remains one Einstein/GHY exterior surface-topography response
counted once, with no core/horizon identification or new boundary law inferred.
