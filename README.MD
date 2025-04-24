# Carlos Compiler

Ce projet implémente un compilateur pour le langage Carlos en Python. Le compilateur est structuré en plusieurs étapes, chacune correspondant à une phase classique de compilation : lexing, parsing, génération d'AST, et visites (par exemple, pour la génération de code ou l'affichage).

## Structure du projet

Le projet est organisé en plusieurs dossiers, chacun correspondant à une étape ou un composant du compilateur :

- **Lexer/** : Contient le code pour l'analyse lexicale.
- **Parser/** : Contient le code pour l'analyse syntaxique et la génération de l'AST.
- **Visitors/** : Contient des visiteurs pour parcourir l'AST, comme un pretty-printer ou un générateur de code JavaScript.
- **examples/** : Contient des exemples de code source en Carlos.
- **Lexer/examples_lexed/** : Contient les résultats de l'analyse lexicale des exemples.
- **Parser/examples_parsed/** : Contient les AST générés à partir des exemples.

---

## Étapes de compilation

### 1. Analyse lexicale (Lexer)

L'analyse lexicale transforme le code source brut en une liste de lexèmes (tokens). Ces lexèmes représentent les plus petites unités syntaxiques du langage (mots-clés, identifiants, opérateurs, etc.).

- **Fichier principal** : `Lexer/lexer.py`
- **Exemple d'utilisation** :
  ```bash
  python3 Lexer/lexer.py examples/hello.carlos --save
  ```
  Cela génère un fichier contenant la représentation des lexems dans le dossier examples_lexed.

### 2. Analyse syntaxique (Parser)

L'analyse syntaxique prend les lexèmes produits par le lexer et construit un arbre syntaxique abstrait (AST). Cet AST représente la structure hiérarchique du programme.

- **Fichier principal** : `Parser/parser.py`
- **Exemple d'utilisation** :
  ```bash
  python3 Parser/parser.py examples/hello.carlos --save
  ```
  Cela génère un fichier contenant l'AST dans le dossier `examples_parsed`.

---

### 3. Visiteurs (Visitors)

Les visiteurs parcourent l'AST pour effectuer diverses tâches, comme :

- **Pretty-printer** : Génère une version formatée du code source.
  - **Fichier** : `Visitors/PrettyPrinter.py`
- **Générateur de code JavaScript** : Convertit le code Carlos en JavaScript.
  - **Fichier** : `Visitors/JSCodeGenerator.py`

Exemple d'utilisation pour le pretty-printer :

```bash
python3 Visitors/PrettyPrinter.py examples/hello.carlos --save
```

---

## Exemples

Des exemples de code source en Carlos sont disponibles dans le dossier `examples`. Voici un exemple simple :

```carlos
function helloWorld() {
  print("Hello, World!");
}
```

Pour tester les différentes étapes de compilation sur cet exemple, utilisez les commandes suivantes :

1. **Analyse lexicale** :

   ```bash
   python3 Lexer/lexer.py examples/hello.carlos --save
   ```

2. **Analyse syntaxique** :

   ```bash
   python3 Parser/parser.py examples/hello.carlos --save
   ```

3. **Pretty-print** :
   ```bash
   python3 Visitors/PrettyPrinter.py examples/hello.carlos --save
   ```

---

## Objectif du projet

L'objectif principal est de convertir le code Carlos en JavaScript pour permettre son exécution. Ce projet peut également servir de base pour apprendre les concepts de compilation.

---

- https://cs.lmu.edu/~ray/notes/carlos/
- https://github.com/rtoal/carlos/
