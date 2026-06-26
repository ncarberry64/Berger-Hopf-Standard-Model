(* Local execution script only.
   Requires Mathematica and FeynRules.
   Does not run in repository tests unless explicitly invoked by the user. *)

Print["BHSM Phase Three-L local model check"];
Print["Loading FeynRules package..."];
Get["FeynRules`"];

Print["Loading BHSM minimal collider-interface model..."];
LoadModel["models/feynrules/BHSM_Minimal_Collider_Interface.fr"];

Print["Model loaded. User must now inspect classes, parameters, and Lagrangian symbols."];

