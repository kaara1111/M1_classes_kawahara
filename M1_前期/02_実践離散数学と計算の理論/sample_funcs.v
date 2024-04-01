Require Import List.
Import ListNotations.

(*
 * succ 7
 * \u3068\u3059\u308b\u3068\u30017 + 1\u3055\u308c\u308b
 *)
Definition succ (n:list nat) : nat :=
  match n with
  | n'::_ => S n'
  | _ => O
  end.

(*
 * proj 0
 * \u3068\u3059\u308b\u3068\u30010\u756a\u76ee\u306e\u5f15\u6570\u3092\u8fd4\u3059\u5c04\u5f71\u3068\u306a\u308b
 * \u4f8b\uff1a
 *   proj 2 [30; 9; 7; 45]
 *   \u306f
 *   7
 *   \u3068\u306a\u308b
 *)
Definition proj (n:nat) (l:list nat) : nat :=
  nth n l O.

(*
 * \u5408\u6210\u95a2\u6570 compose \u306e\u305f\u3081\u306e\u88dc\u52a9\u95a2\u6570
 * \u95a2\u6570\u306e\u30ea\u30b9\u30c8gs\u3001\u95a2\u6570\u3078\u6e21\u3059\u5f15\u6570\u306e\u30ea\u30b9\u30c8args\u3001\u7d50\u679c\u3092\u683c\u7d0d\u3059\u308b\u30ea\u30b9\u30c8l\u3092\u53d7\u3051\u53d6\u3063\u3066
 * \u7d50\u679c\u306e\u30ea\u30b9\u30c8\u3092\u8fd4\u3059
 * \u4f8b\uff1a
 *   gs = [g0; g1; g2]
 *   args = [30, 1, 4]
 *   l = []
 *   \u3068\u3059\u308b\u3068
 *   [(g0 [30, 1, 4]); (g1 [30, 1, 4]); (g2 [30, 1, 4])]
 *   \u304c\u8fd4\u308b
 *)
Fixpoint app_gs (gs:list ((list nat) -> nat)) (args:list nat) (l:list nat): (list nat) :=
  match gs with
  | h::t => app_gs t args ((h args)::l)
  | [] => rev l (* rev\u306f\u30ea\u30b9\u30c8\u3092\u9006\u9806\u306b\u3059\u308b\u95a2\u6570 *)
  end.

(*
 * \u5408\u6210\u95a2\u6570\u3002
 * app_gs\u306e\u7d50\u679c\u306b\u95a2\u6570f\u3092\u9069\u7528\u3057\u3066\u3044\u308b\u306e\u307f
 *)
Definition compose
           (f:(list nat) -> nat)
           (gs:list ((list nat) -> nat))
           (args:list nat)
  : nat :=
  f (app_gs gs args []).

Compute compose succ [proj 1] [2;3].  

Definition shift (n:nat): list nat :=
  [n].

(*
 * \u539f\u59cb\u5e30\u7d0d\u6cd5\u306e0\u756a\u76ee\u306e\u5f15\u6570\u3068\u3001\u6b8b\u308a\u306e\u5f15\u6570\u3092\u5206\u89e3\u3057\u3066\u53d7\u3051\u53d6\u308a\u518d\u5e30\u3059\u308b\u95a2\u6570
 * recurse f g [x0; x1; x2]
 * \u3068\u306a\u3063\u3066\u3044\u305f\u5834\u5408\u3001
 * recurse' f g x0 [x1; x2]
 * \u3068\u547c\u3070\u308b\u3002
 *
 * x0\u3092\u30c7\u30af\u30ea\u30e1\u30f3\u30c8\u3057\u3066\u3044\u304d\u3001\u518d\u5e30\u7684\u306b\u95a2\u6570\u3092\u9069\u7528\u3055\u305b\u3066\u3044\u308b
 *)
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
  | [] => O (* \u30a8\u30e9\u30fc\u3002\u5f15\u6570\u304c\u7121\u3044\u3002 *)
  end.

(*
 * \u539f\u59cb\u5e30\u7d0d\u7684\u95a2\u6570\u306e\u5b9a\u7fa9\u4f8b
 *)
Definition plus (l:list nat): nat :=
  match l with
  | a::b::[] =>
    let f := proj 0 in
    let g := compose succ [proj 1] in
    recurse f g [a; b]
  | _ => 0 (* \u30a8\u30e9\u30fc\u3002plus\u95a2\u6570\u306e\u5f15\u6570\u306f\u5fc5\u305a2\u3064\u3067\u3042\u308b\u3002 *)
  end.

(* plus\u95a2\u6570\u306e\u5b9f\u884c\u4f8b *)
Compute plus [2; 5].

Definition prop0 :forall (A:Prop),A->A:=
  fun A x =>x.

(* True\u3068False\u3092\u5b9a\u7fa9 *)
Definition T: nat := O.
Definition F: nat := S O.

(* if\u5f0f\u306e\u4f8b *)
Definition If (l:list nat): nat :=
  match l with
  | cond::e1::e2::[] =>
    match cond with
    | O => e1 (* T\u306e\u5834\u5408 *)
    | _ => e2 (* T\u4ee5\u5916 *)
    end
  | _ => O (* \u30a8\u30e9\u30fc\u3002if\u5f0f\u306e\u5f15\u6570\u306f\u5fc5\u305a2\u3064\u3067\u3042\u308b\u3002 *)
  end.

(* if\u5f0f\u306e\u5b9f\u884c\u4f8b *)
Compute If [T; 20; 40].

(*Definition pred(n:list nat): nat :=
  match n with
  | _ => 0
  | S n' => n'::_
  end.

Compute pred 4.

Definition mul(l:list nat): nat :=
  match l with
  | a::b::[] =>
    let f := proj 0 in
    let g := compose pred [proj 1] in
    recurse f g [a;b]
  | _ => 0
  end.
*)

Definition pred (n:nat) : nat :=
  match n with
  | 0 => 0
  | S n' => n'
  end.

Fixpoint new_plus(n:nat) (m:nat): nat :=
  match n with
  | 0 => m
  | S n' => S (new_plus n' m)
  end.

Fixpoint mul(n m:nat) : nat :=
  match n with
  | 0 => 0
  | S n' => new_plus m (mul n' m)
  end.

Compute pred 0.
Compute new_plus 2 3.
Compute mul 0 3.

  