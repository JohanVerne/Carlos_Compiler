Grammaire du langage Carlos (extrait de https://cs.lmu.edu/~ray/notes/carlos/):

Carlos {

    Program = Statement+

    Statement = VarDecl
    | TypeDecl
    | FunDecl
    | Exp9 ("++" | "--") ";" --bump
    | Exp9 "=" Exp ";" --assign
    | Exp9_call ";" --call
    | break ";" --break
    | return Exp ";" --return
    | return ";" --shortreturn
    | IfStmt
    | LoopStmt

    VarDecl = (let | const) id "=" Exp ";"
    TypeDecl = struct id "{" Field\* "}"
    Field = id ":" Type
    FunDecl = function id Params (":" Type)? Block
    Params = "(" ListOf<Param, ","> ")"
    Param = id ":" Type

    Type = Type "?" --optional
    | "[" Type "]" --array
    | "(" ListOf<Type, ","> ")" "->" Type --function
    | id --id

    IfStmt = if Exp Block else Block --long
    | if Exp Block else IfStmt --elsif
    | if Exp Block --short
    LoopStmt = while Exp Block --while
    | repeat Exp Block --repeat
    | for id in Exp ("..." | "..<") Exp Block --range
    | for id in Exp Block --collection
    Block = "{" Statement\* "}"

    Exp = Exp1 "?" Exp1 ":" Exp --conditional
    | Exp1
    Exp1 = Exp1 "??" Exp2 --unwrapelse
    | Exp2
    Exp2 = Exp3 ("||" Exp3)+ --or
    | Exp3 ("&&" Exp3)+ --and
    | Exp3
    Exp3 = Exp4 ("|" Exp4)+ --bitor
    | Exp4 ("^" Exp4)+ --bitxor
    | Exp4 ("&" Exp4)+ --bitand
    | Exp4
    Exp4 = Exp5 ("<="|"<"|"=="|"!="|">="|">") Exp5 --compare
    | Exp5
    Exp5 = Exp5 ("<<" | ">>") Exp6 --shift
    | Exp6
    Exp6 = Exp6 ("+" | "-") Exp7 --add
    | Exp7
    Exp7 = Exp7 ("\*"| "/" | "%") Exp8 --multiply
    | Exp8
    Exp8 = Exp9 "\*\*" Exp8 --power
    | Exp9
    | ("#" | "-" | "!" | some | random) Exp9 --unary
    Exp9 = true ~mut
    | false ~mut
    | floatlit ~mut
    | intlit ~mut
    | no Type ~mut --emptyopt
    | Exp9 "(" ListOf<Exp, ","> ")" ~mut --call
    | Exp9 "[" Exp "]" --subscript
    | Exp9 ("." | "?.") id --member
    | stringlit ~mut
    | id --id
    | Type_array "(" ")" ~mut --emptyarray
    | "[" NonemptyListOf<Exp, ","> "]" ~mut --arrayexp
    | "(" Exp ")" ~mut --parens

    intlit = digit+
    floatlit = digit+ "." digit+ (("E" | "e") ("+" | "-")? digit+)?
    stringlit = "\"" char\* "\""
    char = ~control ~"\\" ~"\"" any
    | "\\" ("n" | "t" | "\"" | "\\") --escape
    | "\\u{" hex hex? hex? hex? hex? hex? "}" --codepoint
    control = "\x00".."\x1f" | "\x80".."\x9f"
    hex = hexDigit
    mut = ~"==" "=" | "++" | "--"

    let = "let" ~alnum
    const = "const" ~alnum
    struct = "struct" ~alnum
    function = "function" ~alnum
    if = "if" ~alnum
    else = "else" ~alnum
    while = "while" ~alnum
    repeat = "repeat" ~alnum
    for = "for" ~alnum
    in = "in" ~alnum
    random = "random" ~alnum
    break = "break" ~alnum
    return = "return" ~alnum
    some = "some" ~alnum
    no = "no" ~alnum
    true = "true" ~alnum
    false = "false" ~alnum
    keyword = let | const | struct | function | if | else | while | repeat
    | for | in | break | return | some | no | random | true | false
    id = ~keyword letter alnum\*

    space += "//" (~"\n" any)\* --comment

}
