Require Import List.
Import ListNotations.

 (*
Inductive nat:Set :=
| O : nat
| S : nat -> nat.

Compute S (S O).
*)


Definition hd (default:nat) (l:list nat) : nat :=
  match l with
  | nil => default
  | h :: t => h
  end.

Definition tail (l:list nat) : list nat:=
  match l with
  | nil => nil
  | h :: t => t
  end.



(* Compute hd 0 [1;2;3]. *)
Example test_hd1:             hd 0 [1;2;3] = 1.
Proof. reflexivity.  Qed.
Example test_hd2:             hd 0 [] = 0.
Proof. reflexivity.  Qed.
Example test_tail:            tail [1;2;3] = [2;3].
Proof. reflexivity.  Qed.




Definition succ (n:list nat) : nat :=
  match n with
  | n'::_=> S n'
  | _ => 0
  end.

Compute (succ [5;6;7]).



Definition proj (n:nat) (l:list nat) : nat :=
  nth n l O.

Compute (proj 2 [1;3;5;7;9]).


Fixpoint app_gs (gs:list ((list nat) -> nat)) (args:list nat) (l:list nat): (list nat) :=
  match gs with
  | h::t => app_gs t args ((h args)::l)
  | [] => rev l (* rev is a function to invert list *)
  end.

Definition compose
           (f:(list nat) -> nat)
           (gs:list ((list nat) -> nat))
           (args:list nat)
  : nat :=
  f (app_gs gs args []).



Fixpoint recurse'
         (f:(list nat) -> nat) (* f(x1, ..., xn) *)
         (g:(list nat) -> nat) (* g(n, h(n, x1, ..., xn), x1, ..., xn) *)
         (x0:nat)
         (args:list nat) (* x1 ... xn *)
  : nat :=
  match x0 with
  | O => f args
  | S n => g (n :: (recurse' f g n args) :: args)
  end.



Definition recurse
           (f:(list nat) -> nat) (* f(x1, ..., xn) *)
           (g:(list nat) -> nat) (* g(n, h(n, x1, ..., xn), x1, ..., xn) *)
           (args:list nat) (* x0 ... xn *)
  : nat :=
  match args with
  | h::t => recurse' f g h t
  | [] => O
  end.



Definition plus (l:list nat): nat :=
  match l with
  | a::b::[] =>
    let f := proj 0 in
    let g := compose succ [proj 1] in
    recurse f g [a; b]
  | _ => 0 (* \u30a8\u30e9\u30fc\u3002plus\u95a2\u6570\u306e\u5f15\u6570\u306f\u5fc5\u305a2\u3064\u3067\u3042\u308b\u3002 *)
  end.



