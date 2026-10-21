import Imscribing.Primitives.Imscription
import Imscribing.GeneticCode
open Imscribing.Primitives
def rebisBase : Imscription := {
  dim := .dead,
  top := .judge,
  rel := .ado,
  pol := .church,
  fid := .age,
  kin := .yea,
  gran := .bib,
  gram := .vow,
  crit := .woe,
  chir := .fee,
  stoi := .hung,
  prot := .awe,
}
def rebis_dim : List Dimensionality := [.dead, .ash, .array, .if']
#eval do
  let values := rebis_dim
  let glyphs := String.join (values.map (fun (x : Dimensionality) => Dimensionality.shavian x))
  let tensor := String.join (values.flatMap (fun (a : Dimensionality) => values.map (fun (b : Dimensionality) => ((tensorProduct { rebisBase with dim := a } { rebisBase with dim := b }).dim).shavian)))
  let meet := String.join (values.flatMap (fun (a : Dimensionality) => values.map (fun (b : Dimensionality) => Dimensionality.shavian (meetPrimitive a b))))
  let join := String.join (values.flatMap (fun (a : Dimensionality) => values.map (fun (b : Dimensionality) => Dimensionality.shavian (joinPrimitive a b))))
  IO.println ("AXIS\t⊢\t" ++ glyphs ++ "\t" ++ tensor ++ "\t" ++ meet ++ "\t" ++ join)

def rebis_top : List Topology := [.judge, .eat, .mime, .oil, .are]
#eval do
  let values := rebis_top
  let glyphs := String.join (values.map (fun (x : Topology) => Topology.shavian x))
  let tensor := String.join (values.flatMap (fun (a : Topology) => values.map (fun (b : Topology) => ((tensorProduct { rebisBase with top := a } { rebisBase with top := b }).top).shavian)))
  let meet := String.join (values.flatMap (fun (a : Topology) => values.map (fun (b : Topology) => Topology.shavian (meetPrimitive a b))))
  let join := String.join (values.flatMap (fun (a : Topology) => values.map (fun (b : Topology) => Topology.shavian (joinPrimitive a b))))
  IO.println ("AXIS\t⊣\t" ++ glyphs ++ "\t" ++ tensor ++ "\t" ++ meet ++ "\t" ++ join)

def rebis_rel : List Relational := [.ado, .tot, .ear, .ian]
#eval do
  let values := rebis_rel
  let glyphs := String.join (values.map (fun (x : Relational) => Relational.shavian x))
  let tensor := String.join (values.flatMap (fun (a : Relational) => values.map (fun (b : Relational) => ((tensorProduct { rebisBase with rel := a } { rebisBase with rel := b }).rel).shavian)))
  let meet := String.join (values.flatMap (fun (a : Relational) => values.map (fun (b : Relational) => Relational.shavian (meetPrimitive a b))))
  let join := String.join (values.flatMap (fun (a : Relational) => values.map (fun (b : Relational) => Relational.shavian (joinPrimitive a b))))
  IO.println ("AXIS\t≻\t" ++ glyphs ++ "\t" ++ tensor ++ "\t" ++ meet ++ "\t" ++ join)

def rebis_pol : List Polarity := [.church, .yew, .out, .nun, .or']
#eval do
  let values := rebis_pol
  let glyphs := String.join (values.map (fun (x : Polarity) => Polarity.shavian x))
  let tensor := String.join (values.flatMap (fun (a : Polarity) => values.map (fun (b : Polarity) => ((tensorProduct { rebisBase with pol := a } { rebisBase with pol := b }).pol).shavian)))
  let meet := String.join (values.flatMap (fun (a : Polarity) => values.map (fun (b : Polarity) => Polarity.shavian (meetPrimitive a b))))
  let join := String.join (values.flatMap (fun (a : Polarity) => values.map (fun (b : Polarity) => Polarity.shavian (joinPrimitive a b))))
  IO.println ("AXIS\t≺\t" ++ glyphs ++ "\t" ++ tensor ++ "\t" ++ meet ++ "\t" ++ join)

def rebis_fid : List Fidelity := [.age, .they, .peep]
#eval do
  let values := rebis_fid
  let glyphs := String.join (values.map (fun (x : Fidelity) => Fidelity.shavian x))
  let tensor := String.join (values.flatMap (fun (a : Fidelity) => values.map (fun (b : Fidelity) => ((tensorProduct { rebisBase with fid := a } { rebisBase with fid := b }).fid).shavian)))
  let meet := String.join (values.flatMap (fun (a : Fidelity) => values.map (fun (b : Fidelity) => Fidelity.shavian (meetPrimitive a b))))
  let join := String.join (values.flatMap (fun (a : Fidelity) => values.map (fun (b : Fidelity) => Fidelity.shavian (joinPrimitive a b))))
  IO.println ("AXIS\t⋈\t" ++ glyphs ++ "\t" ++ tensor ++ "\t" ++ meet ++ "\t" ++ join)

def rebis_kin : List KineticChar := [.yea, .loll, .egg, .on, .air]
#eval do
  let values := rebis_kin
  let glyphs := String.join (values.map (fun (x : KineticChar) => KineticChar.shavian x))
  let tensor := String.join (values.flatMap (fun (a : KineticChar) => values.map (fun (b : KineticChar) => ((tensorProduct { rebisBase with kin := a } { rebisBase with kin := b }).kin).shavian)))
  let meet := String.join (values.flatMap (fun (a : KineticChar) => values.map (fun (b : KineticChar) => KineticChar.shavian (meetPrimitive a b))))
  let join := String.join (values.flatMap (fun (a : KineticChar) => values.map (fun (b : KineticChar) => KineticChar.shavian (joinPrimitive a b))))
  IO.println ("AXIS\t⊤\t" ++ glyphs ++ "\t" ++ tensor ++ "\t" ++ meet ++ "\t" ++ join)

def rebis_gran : List Granularity := [.bib, .thigh, .ice]
#eval do
  let values := rebis_gran
  let glyphs := String.join (values.map (fun (x : Granularity) => Granularity.shavian x))
  let tensor := String.join (values.flatMap (fun (a : Granularity) => values.map (fun (b : Granularity) => ((tensorProduct { rebisBase with gran := a } { rebisBase with gran := b }).gran).shavian)))
  let meet := String.join (values.flatMap (fun (a : Granularity) => values.map (fun (b : Granularity) => Granularity.shavian (meetPrimitive a b))))
  let join := String.join (values.flatMap (fun (a : Granularity) => values.map (fun (b : Granularity) => Granularity.shavian (joinPrimitive a b))))
  IO.println ("AXIS\t∈\t" ++ glyphs ++ "\t" ++ tensor ++ "\t" ++ meet ++ "\t" ++ join)

def rebis_gram : List Grammar := [.vow, .gag, .measure, .ooze]
#eval do
  let values := rebis_gram
  let glyphs := String.join (values.map (fun (x : Grammar) => Grammar.shavian x))
  let tensor := String.join (values.flatMap (fun (a : Grammar) => values.map (fun (b : Grammar) => ((tensorProduct { rebisBase with gram := a } { rebisBase with gram := b }).gram).shavian)))
  let meet := String.join (values.flatMap (fun (a : Grammar) => values.map (fun (b : Grammar) => Grammar.shavian (meetPrimitive a b))))
  let join := String.join (values.flatMap (fun (a : Grammar) => values.map (fun (b : Grammar) => Grammar.shavian (joinPrimitive a b))))
  IO.println ("AXIS\t∋\t" ++ glyphs ++ "\t" ++ tensor ++ "\t" ++ meet ++ "\t" ++ join)

def rebis_crit : List Criticality := [.woe, .monad, .roar, .err, .haha]
#eval do
  let values := rebis_crit
  let glyphs := String.join (values.map (fun (x : Criticality) => Criticality.shavian x))
  let tensor := String.join (values.flatMap (fun (a : Criticality) => values.map (fun (b : Criticality) => ((tensorProduct { rebisBase with crit := a } { rebisBase with crit := b }).crit).shavian)))
  let meet := String.join (values.flatMap (fun (a : Criticality) => values.map (fun (b : Criticality) => Criticality.shavian (meetPrimitive a b))))
  let join := String.join (values.flatMap (fun (a : Criticality) => values.map (fun (b : Criticality) => Criticality.shavian (joinPrimitive a b))))
  IO.println ("AXIS\t⊙\t" ++ glyphs ++ "\t" ++ tensor ++ "\t" ++ meet ++ "\t" ++ join)

def rebis_chir : List Chirality := [.fee, .kick, .sure, .wool]
#eval do
  let values := rebis_chir
  let glyphs := String.join (values.map (fun (x : Chirality) => Chirality.shavian x))
  let tensor := String.join (values.flatMap (fun (a : Chirality) => values.map (fun (b : Chirality) => ((tensorProduct { rebisBase with chir := a } { rebisBase with chir := b }).chir).shavian)))
  let meet := String.join (values.flatMap (fun (a : Chirality) => values.map (fun (b : Chirality) => Chirality.shavian (meetPrimitive a b))))
  let join := String.join (values.flatMap (fun (a : Chirality) => values.map (fun (b : Chirality) => Chirality.shavian (joinPrimitive a b))))
  IO.println ("AXIS\t⊥\t" ++ glyphs ++ "\t" ++ tensor ++ "\t" ++ meet ++ "\t" ++ join)

def rebis_stoi : List Stoichiometry := [.hung, .so, .up]
#eval do
  let values := rebis_stoi
  let glyphs := String.join (values.map (fun (x : Stoichiometry) => Stoichiometry.shavian x))
  let tensor := String.join (values.flatMap (fun (a : Stoichiometry) => values.map (fun (b : Stoichiometry) => ((tensorProduct { rebisBase with stoi := a } { rebisBase with stoi := b }).stoi).shavian)))
  let meet := String.join (values.flatMap (fun (a : Stoichiometry) => values.map (fun (b : Stoichiometry) => Stoichiometry.shavian (meetPrimitive a b))))
  let join := String.join (values.flatMap (fun (a : Stoichiometry) => values.map (fun (b : Stoichiometry) => Stoichiometry.shavian (joinPrimitive a b))))
  IO.println ("AXIS\t⊞\t" ++ glyphs ++ "\t" ++ tensor ++ "\t" ++ meet ++ "\t" ++ join)

def rebis_prot : List Protection := [.awe, .oak, .ah, .zoo]
#eval do
  let values := rebis_prot
  let glyphs := String.join (values.map (fun (x : Protection) => Protection.shavian x))
  let tensor := String.join (values.flatMap (fun (a : Protection) => values.map (fun (b : Protection) => ((tensorProduct { rebisBase with prot := a } { rebisBase with prot := b }).prot).shavian)))
  let meet := String.join (values.flatMap (fun (a : Protection) => values.map (fun (b : Protection) => Protection.shavian (meetPrimitive a b))))
  let join := String.join (values.flatMap (fun (a : Protection) => values.map (fun (b : Protection) => Protection.shavian (joinPrimitive a b))))
  IO.println ("AXIS\t⊡\t" ++ glyphs ++ "\t" ++ tensor ++ "\t" ++ meet ++ "\t" ++ join)

open Imscribing.GeneticCode
def rebisPrimitiveMark : IGPrimitive → String
  | .Dimensionality => "⊢" | .Topology => "⊣" | .Recognition => "≻"
  | .Parity => "≺" | .Fidelity => "⋈" | .Kinetics => "⊤"
  | .Granularity => "∈" | .Coupling => "∋" | .Criticality => "⊙"
  | .Chirality => "⊥" | .Stoichiometry => "⊞" | .Winding => "⊡"
#eval IO.println ("AA\tAla\t" ++ ((aaToPrimitive .Ala).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tArg\t" ++ ((aaToPrimitive .Arg).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tAsn\t" ++ ((aaToPrimitive .Asn).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tAsp\t" ++ ((aaToPrimitive .Asp).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tCys\t" ++ ((aaToPrimitive .Cys).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tGln\t" ++ ((aaToPrimitive .Gln).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tGlu\t" ++ ((aaToPrimitive .Glu).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tGly\t" ++ ((aaToPrimitive .Gly).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tHis\t" ++ ((aaToPrimitive .His).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tIle\t" ++ ((aaToPrimitive .Ile).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tLeu\t" ++ ((aaToPrimitive .Leu).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tLys\t" ++ ((aaToPrimitive .Lys).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tMet\t" ++ ((aaToPrimitive .Met).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tPhe\t" ++ ((aaToPrimitive .Phe).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tPro\t" ++ ((aaToPrimitive .Pro).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tSer\t" ++ ((aaToPrimitive .Ser).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tThr\t" ++ ((aaToPrimitive .Thr).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tTrp\t" ++ ((aaToPrimitive .Trp).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tTyr\t" ++ ((aaToPrimitive .Tyr).map rebisPrimitiveMark).getD "-")
#eval IO.println ("AA\tVal\t" ++ ((aaToPrimitive .Val).map rebisPrimitiveMark).getD "-")
