(* Local execution script only.
   Requires Mathematica and FeynRules.
   This is a handoff runner, not repository validation evidence. *)

Print["BHSM Phase Three-L local UFO export runner"];
Get["FeynRules`"];
LoadModel["models/feynrules/BHSM_Minimal_Collider_Interface.fr"];

Print["Attempting UFO export for L_BHSM_Minimal..."];
WriteUFO[L_BHSM_Minimal, Output -> "models/ufo/BHSM_Minimal_Collider_Interface"];

