//! Local Python adapter to the canonical Vox peptide implementation.
#![allow(dead_code)]
extern crate alloc;
#[path = "../../Vox/src/fold3d.rs"] mod fold3d;
#[path = "../../Vox/src/peptide_geometry.rs"] mod peptide_geometry;
#[path = "../../Vox/src/peptide_closure.rs"] mod peptide_closure;
#[path = "../../Vox/src/phase_word.rs"] mod phase_word;
#[path = "../../Vox/src/protein_relax.rs"] mod protein_relax;
#[path = "../../Vox/src/fold.rs"] mod fold;
use std::io::{self,Read};
fn quote(value:&str)->String {
 let mut out=String::from("\"");
 for c in value.chars(){match c{'"'=>out.push_str("\\\""),'\\'=>out.push_str("\\\\"),'\n'=>out.push_str("\\n"),'\r'=>out.push_str("\\r"),'\t'=>out.push_str("\\t"),c if c<' '=>out.push_str(&format!("\\u{:04x}",c as u32)),c=>out.push(c)}}
 out.push('"');out
}
fn number(x:f64)->String {if x.is_finite(){format!("{:.17}",x)}else{String::from("null")}}
fn point(p:peptide_geometry::Point)->String {format!("[{},{},{}]",number(p.0),number(p.1),number(p.2))}
fn main()->Result<(),Box<dyn std::error::Error>> {
 let mut input=String::new();io::stdin().read_to_string(&mut input)?;
 if std::env::args().nth(1).as_deref()==Some("--words") {
  let mut rows=Vec::new();
  for line in input.lines().filter(|s|!s.is_empty()) {
   let (word,tuple)=line.split_once('\t').ok_or("missing self-mark payload")?;
   let read=phase_word::execute(word,&tuple.to_string())?;
   let payloads=read.surviving.iter().map(|d|format!("{{\"id\":{},\"lane\":{},\"tuple\":{}}}",d.id,d.lane,quote(&d.observation))).collect::<Vec<_>>().join(",");
   rows.push(format!("{{\"register\":{},\"surviving\":[{}],\"cleared\":{},\"restored\":{},\"exposed\":{},\"deposits\":{},\"inert\":{},\"native_transition_table\":{:?}}}",read.register,payloads,read.cleared,read.restored,read.exposed,read.deposits,read.inert,phase_word::native_transition_table(word)?));
  }
  println!("[{}]",rows.join(","));return Ok(());
 }
 let assessing=std::env::args().nth(1).as_deref()==Some("--assess");
 let (geometry_input,word_text)=input.split_once("\nFOLD_WORDS\n").unwrap_or((input.as_str(),""));
 let (header,coordinate_text)=if assessing {geometry_input.split_once("\nCOORDINATES\n").ok_or("missing coordinate boundary")?}else{(geometry_input,"")};
 let rows:Vec<_>=header.lines().filter(|s|!s.trim().is_empty()).map(|s|s.split_whitespace().collect::<Vec<_>>()).collect();
 let mut steps=Vec::new();let mut chain=Vec::new();let mut source=Vec::new();let mut retained=Vec::new();
 for row in &rows {
  if row.len()!=5 {return Err("expected AA phi psi sequence_label backbone_label per residue".into());}
  let (phi,psi)=(row[1].parse::<f64>()?,row[2].parse::<f64>()?);
  if !phi.is_finite()||!psi.is_finite(){return Err("nonfinite input torsion".into());}
  let ss=match row[4]{"helix"=>"helix","helix_l"=>"helix_l","sheet"=>"sheet","turn"=>"turn","loop"=>"loop",_=>"other"};
  steps.push(fold3d::RamaEntry{phi,psi,ss,conf:0.0});chain.push(row[0]);source.push(row[3]);retained.push(row[4]);
 }
 if chain.iter().any(|aa|! ["Ala","Arg","Asn","Asp","Cys","Gln","Glu","Gly","His","Ile","Leu","Lys","Met","Phe","Pro","Ser","Thr","Trp","Tyr","Val"].contains(aa)){return Err("unknown standard residue".into());}
 let mut bb=fold3d::build_backbone(&steps);
 let mut folding=String::from("null");
 if !word_text.is_empty() && !assessing {
  let names=["Ala","Arg","Asn","Asp","Cys","Gln","Glu","Gly","His","Ile","Leu","Lys","Met","Phe","Pro","Ser","Thr","Trp","Tyr","Val"];
  let static_chain:Vec<_>=chain.iter().map(|aa|*names.iter().find(|name|*name==aa).unwrap()).collect();
  let mut words=vec![Vec::new();chain.len()];
  for line in word_text.lines() {
   let (index,word)=line.split_once(' ').ok_or("invalid fold form row")?;
   let index=index.parse::<usize>()?;
   if index>=words.len(){return Err("fold form outside residue boundary".into());}
   words[index].push(word);
  }
  let relations=fold::fold_sequence(&static_chain);
  let contacts:Vec<_>=relations.contacts.iter().map(|c|protein_relax::Contact{i:c.i,j:c.j}).collect();
  let result=protein_relax::run(&chain,&steps,&contacts,&words,160)?;
  folding=format!("{{\"initial_score\":{},\"final_score\":{},\"accepted\":{},\"word_calls\":{},\"payload_moves\":{}}}",result.initial,result.final_score,result.accepted,result.word_calls,result.payload_moves);
  steps=result.steps;bb=result.backbone;
 }
 let mut sidechains:Vec<Vec<(&str,_)>>=chain.iter().zip(&bb).zip(&steps).map(|((aa,b),s)|fold3d::build_sidechain(aa,b,s)).collect();
 if assessing {
  let mut frames=vec![[None;4];chain.len()];sidechains.iter_mut().for_each(|sc|sc.clear());
  for line in coordinate_text.lines().filter(|l|!l.trim().is_empty()) {
   let fields:Vec<_>=line.split_whitespace().collect();if fields.len()!=5 {return Err("invalid coordinate row".into());}
   let i=fields[0].parse::<usize>()?;if i>=chain.len(){return Err("coordinate residue out of range".into());}
   let xyz=(fields[2].parse::<f64>()?,fields[3].parse::<f64>()?,fields[4].parse::<f64>()?);
   if let Some(slot)=["N","CA","C","O"].iter().position(|&name|name==fields[1]) {
    if frames[i][slot].replace(xyz).is_some(){return Err("duplicate backbone atom".into());}
   } else {sidechains[i].push((fields[1],xyz));}
  }
  for (i,frame) in frames.into_iter().enumerate() {
   if frame.iter().any(|p|p.is_none()){return Err("missing backbone atom".into());}
   bb[i]=fold3d::BackboneAtom{n:frame[0].unwrap(),ca:frame[1].unwrap(),c:frame[2].unwrap(),o:frame[3].unwrap()};
  }
 }
 let coords:Vec<_>=bb.iter().map(|b|[b.n,b.ca,b.c,b.o]).collect();
 let angles:Vec<_>=steps.iter().map(|s|(s.phi,s.psi)).collect();
 let evidence=peptide_closure::assess(&chain,&coords,&sidechains,&angles);
 let secondary:Vec<_>=source.iter().zip(&retained).enumerate().map(|(i,(&left,&right))| {
  let l:Vec<_>=if left=="-" {vec![]}else{vec![left]};
  let r:Vec<_>=if right=="-" {vec![]}else{vec![right]};
  let mut e=peptide_closure::secondary_evidence(&l,&r).into_iter().next().unwrap_or(peptide_closure::SecondaryEvidence {
   residue:i+1,sequence:None,backbone:None,helix:peptide_closure::EvidenceState::N,sheet:peptide_closure::EvidenceState::N,other:peptide_closure::EvidenceState::N});
  e.residue=i+1;e
 }).collect();
 let residues:Vec<_>=bb.iter().zip(&sidechains).map(|(b,sc)|format!("{{\"n\":{},\"ca\":{},\"c\":{},\"o\":{},\"sidechain\":[{}]}}",point(b.n),point(b.ca),point(b.c),point(b.o),sc.iter().map(|(name,xyz)|format!("{{\"name\":{},\"xyz\":{}}}",quote(name),point(*xyz))).collect::<Vec<_>>().join(","))).collect();
 let issues=evidence.issues.iter().map(|x|format!("{{\"kind\":{},\"detail\":{}}}",quote(x.kind),quote(&x.detail))).collect::<Vec<_>>().join(",");
 let secondary_rows=secondary.iter().map(|x|format!("{{\"residue\":{},\"sequence\":{},\"backbone\":{},\"helix\":{},\"sheet\":{},\"other\":{}}}",x.residue,quote(x.sequence.unwrap_or("")),quote(x.backbone.unwrap_or("")),quote(&x.helix.mark().to_string()),quote(&x.sheet.mark().to_string()),quote(&x.other.mark().to_string()))).collect::<Vec<_>>().join(",");
 print!("{{\"folding\":{},\"torsions\":[{}],",folding,steps.iter().map(|s|format!("[{},{}]",s.phi,s.psi)).collect::<Vec<_>>().join(","));
 println!("\"residues\":[{}],\"geometry\":{{\"constraints_satisfied\":{},\"atoms\":{},\"bonds\":{},\"angles\":{},\"rings\":{},\"stereocenters\":{},\"backbone_torsions\":{},\"nonbonded_pairs\":{},\"max_bond_error\":{},\"max_overlap\":{},\"issues\":[{}],\"report\":{}}},\"secondary\":[{}],\"secondary_report\":{}}}",residues.join(","),evidence.closed(),evidence.atoms,evidence.bonds,evidence.angles,evidence.rings,evidence.stereocenters,evidence.torsions,evidence.nonbonded_pairs,evidence.max_bond_error,evidence.max_overlap,issues,quote(&evidence.report(true)),secondary_rows,quote(&peptide_closure::secondary_report(&secondary,true)));
 Ok(())
}
