(* Basic types *)
Parameter Entity : Type.
Parameter Event : Type.

Parameter rel : Entity -> Entity -> Prop.
Parameter prog : Prop -> Prop.
Parameter two : Entity -> Prop.
Parameter _people : Entity -> Prop.

(* Temporal operators *)
Parameter hold : Event -> Prop.
Parameter cul : Event -> Prop.
Parameter past : Event -> Prop.
Parameter future : Event -> Prop.

(* Thematic roles *)
Parameter nom : Event -> Entity.
Parameter subj : Event -> Entity.
Parameter top : Event -> Entity.
Parameter acc : Event -> Entity.
Parameter acci : Event -> Prop -> Prop.
Parameter acce : Event -> Event.
Parameter dat : Event -> Entity.
Parameter attr : Event -> Entity.
Parameter deg : Event -> Entity.

(* upper case letters *)
Parameter Subj : Event -> Entity.
Parameter Top : Event -> Entity.
Parameter Acc : Event -> Entity.
Parameter AccI : Event -> Prop -> Prop.
Parameter AccE : Event -> Event.
Parameter Dat : Event -> Entity.
Parameter Attr : Event -> Entity.
Parameter Deg : Event -> Entity.

(* for underspecified terms *)
Parameter ArgOf : Entity -> Entity -> Prop.
Parameter _argof : Entity -> Entity -> Prop.

(* multiwords *)
Parameter _in_front_of : Event -> Entity -> Prop.
Parameter _at_least : Event -> Prop.

(* Generalized quantifiers *)
Parameter most : (Entity -> Prop) -> (Entity -> Prop) -> Prop.

Notation "'Most' x ; P , Q" := (most (fun x => P) (fun x => Q))
   (at level 30, x ident, right associativity) : type_scope.

Axiom most_ex_import :
  forall (F G: Entity -> Prop),
   (most F G -> exists x, F x /\ G x).

Axiom most_consv :
  forall (F G: Entity -> Prop),
   (most F G -> most F (fun x => (F x /\ G x))).

Axiom most_rightup :
  forall (F G H: Entity -> Prop),
   ((most F G) ->
   (forall x, G x -> H x) -> (most F H)).

Hint Resolve most_ex_import most_consv most_rightup.

(* veridical predicates *)
Parameter _true : Prop -> Prop.

Axiom veridical_true : forall P, (_true P -> P).

Ltac solve_veridical_true :=
  match goal with
    H : _true _ |- _
    => try apply veridical_true in H
  end.

(* anti-veridical predicates *)
Parameter _false : Prop -> Prop.

Axiom antiveridical_false : forall P, (_false P -> ~P).

Hint Resolve antiveridical_false.

Ltac solve_antiveridical_false :=
  match goal with
    H : _false _ |- _
    => try apply antiveridical_false in H
  end.

(* implicative verbs *)
Parameter _manage : Event -> Prop.

Axiom implicative_manage : forall v : Event, forall P : Prop, acci v P -> _manage v -> P.

Ltac solve_implicative_manage :=
  match goal with
    H1 : _manage ?v, H2 : acci ?v _ |- _
    => try apply implicative_manage in H2
  end.

Parameter _fail : Event -> Prop.

Axiom implicative_fail :  forall v : Event, forall P : Prop, acci v P -> _fail v -> ~ P.

Ltac solve_implicative_fail :=
  match goal with
    H : _fail ?v, H2 : acci ?v _ |- _
    => try apply implicative_fail in H2
  end.

(* factive verbs *)
Parameter _know : Event -> Prop.

Axiom factive_know : forall v : Event, forall P : Prop, acci v P -> _know v -> P.

Ltac solve_factive :=
  match goal with
    H1 : _know ?v, H2 : acci ?v _ |- _
    => try apply factive_know in H2
  end.

(* privative adjectives *)
Parameter _former : Prop -> Prop.
Axiom privative_former : forall P, (_former P -> ~P).

Ltac solve_privative_former :=
  match goal with
    H : _former _ |- _
    => try apply privative_former in H
  end.

Parameter _fake : Prop -> Prop.
Axiom privative_fake : forall P, (_fake P -> ~P).

Ltac solve_privative_fake :=
  match goal with
    H : _fake _ |- _
    => try apply privative_fake in H
  end.

(* before and after *)
Parameter _before : Event -> Event -> Prop.
Parameter _after : Event -> Event -> Prop.

Axiom transitivity_before : forall v1 v2 v3 : Event,
  _before v1 v2 -> _before v2 v3 -> _before v1 v3.

Axiom transitivity_after : forall v1 v2 v3 : Event,
  _after v1 v2 -> _after v2 v3 -> _after v1 v3.

Axiom before_after : forall v1 v2 : Event,
  _before v1 v2 -> _after v2 v1.

Axiom after_before : forall v1 v2 : Event,
  _after v1 v2 -> _before v2 v1.

Hint Resolve transitivity_before transitivity_after before_after after_before.


(* Preliminary tactics *)

Ltac apply_ent :=
  match goal with
    | [x : Entity, H : forall x : Entity, _ |- _]
     => apply H; clear H
  end.

Ltac eqlem_sub :=
  match goal with
    | [ H1: ?A ?t, H2: forall x, @?D x -> @?C x |- _ ]
     => match D with context[ A ]
         => assert(C t); try (apply H2 with (x:= t)); clear H2
    end
  end.

Axiom unique_role : forall v1 v2 : Event, subj v1 = subj v2 -> v1 = v2.
Ltac resolve_unique_role :=
  match goal with 
    H : subj ?v1 = subj ?v2 |- _
    => repeat apply unique_role in H
  end.

Ltac substitution :=
  match goal with
    | [H1 : _ = ?t |- _ ]
      => try repeat resolve_unique_role; try rewrite <- H1 in *; subst
    | [H1 : ?t = _ |- _ ]
      => try resolve_unique_role; try rewrite H1 in *; subst
  end.

(*
Ltac eqlem_sub :=
  match goal with
    | [ H1: ?A ?t, H2: forall x, _ -> @?C x |- _ ]
     => match type of H2 with context[ A ]
         => assert(C t); try (apply H2); clear H2
    end
  end.
*)

(*
Ltac eqlem_last :=
  match goal with
    | [ H1: _ -> ?B |- _ ]
         => assert(B); try (apply H1); clear H1
  end.
(* bak 1-2-21 *)
*)

Ltac exchange :=
  match goal with
    | [H1 : forall x, _, H2 : forall x, _ |- _]
     => generalize dependent H2
  end.

Ltac exchange_equality :=
  match goal with
    | [H1 : _ = _, H2: _ =  _ |- _]
     => generalize dependent H2
  end.

Ltac clear_pred :=
  match goal with
    | [H1 : ?F ?t, H2 : ?F ?u |- _ ]
     => clear H2
  end.

Ltac solve_false :=
  match goal with
    | [H : _ -> False |- False]
     => apply H
  end.

Axiom urevent : Event.
Ltac ap_event := try apply urevent.


(* Main tactics *)

(*
Ltac eintro :=
  match goal with
   [ H : ?A ?t |- exists x, @?B x /\ _ ]
    => exists t
  end.
*)

Ltac nltac_init :=
  try(intuition;
      try solve_false;
      firstorder;
      repeat subst;
      firstorder).

Ltac nltac_base := 
  try nltac_init;
  try (eauto; eexists; firstorder);
  try repeat substitution;
  try (subst; eauto; firstorder; try congruence);
  try ap_event.

Ltac nltac_axiom :=
 try first
   [solve_veridical_true |
    solve_antiveridical_false |
    solve_implicative_manage |
    solve_implicative_fail |
    solve_factive |
    solve_privative_former |
    solve_privative_fake
   ].

Ltac nltac_set :=
  repeat (nltac_init;
          try repeat substitution;
          try exchange_equality;
          try repeat substitution;  
          (* try apply_ent; *)
          try eqlem_sub).

(*
Ltac nltac_set :=
  repeat (nltac_init; try apply_ent; try eqlem_sub).
*)

Ltac nltac_set_exch :=
  repeat (nltac_init;
          try repeat substitution;
          try apply_ent;
          try exchange;
          try eqlem_sub).

Ltac nltac_final :=
  try solve [repeat nltac_base | clear_pred; repeat nltac_base].

Ltac nltac_final' :=
  try solve
    [repeat nltac_base; ap_event |
     clear_pred; repeat nltac_base; ap_event].

Ltac solve_gq :=
  match goal with
    H : most _ _ |- _
    => let H0 := fresh in
       try solve [         
          pose (H0 := H); eapply most_ex_import in H0;
            try (nltac_set; nltac_final) |
          pose (H0 := H); eapply most_consv in H0;
            eapply most_rightup in H0;
            try (nltac_set; nltac_final) |
          pose (H0 := H); eapply most_consv in H0;
            try (nltac_set; nltac_final) |
          pose (H0 := H); eapply most_rightup in H0;
            try (nltac_set; nltac_final) ]
  end.

(*
Ltac nltac :=
  try solve
    [nltac_set; nltac_final].
*)


Ltac nltac :=
  try solve
    [nltac_set; nltac_final |
     nltac_set_exch; nltac_final |
     nltac_init; solve_gq |
     nltac_set; try nltac_axiom;
     solve [nltac_final | nltac_set; nltac_final]
    ].


(* For BAK:
Ltac nltac :=
  try solve
    [nltac_set; nltac_final |
     nltac_set1; nltac_final |
     nltac_init; solve_gq |
     nltac_init; try nltac_axiom; repeat nltac_base
    ].
*)

