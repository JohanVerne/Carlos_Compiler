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
- **Visitors/examples_js/** : Contient le code JavaScript généré des exemples.
- **Visitors/examples_prettyprinted/** : Contient le code source en Carlos pretty-printed des exemples.

---

## Installation et exécution

Pour utiliser le compilateur, vous devez avoir Python 3 installé, aucune bibliothèque n'est necessaire à l'exécution des différents fichiers.

Vous pouvez cloner le projet depuis GitHub :

```bash
git clone https://github.com/JohanVerne/Carlos_Compiler.git
```

ou télécharger le zip.

Afin de pouvoir compiler intégralement un fichier .carlos jusqu'à leur exécution en tant que fichier JavaScript, vous devez avoir Node.js installé. Vous pouvez obtenir Node.js depuis [https://nodejs.org](https://nodejs.org) ou avec votre package manager favori.
Si vous ne souhaitez pas utiliser Node.js ou possèdez un interpréteur JavaScript différent, vous ne pourrez pas utiliser le fichier `compiler.py` pour exécuter le code JavaScript généré à partir du .carlos. Cependant, vous pouvez utiliser le fichier `Visitors/JSCodeGenerator.py` pour obtenir le code JavaScript et l'exécuter de votre manière désirée.

## Étapes de compilation

### 1. Analyse lexicale (Lexer)

L'analyse lexicale transforme le code source brut en une liste de lexèmes (tokens). Ces lexèmes représentent les plus petites unités syntaxiques du langage (mots-clés, identifiants, opérateurs, etc.).

- **Fichier principal** : `Lexer/lexer.py`
- **Exemple d'utilisation** :
  ```bash
  python3 Lexer/lexer.py examples/hello.carlos
  ```
  Cela affiche les lexems dans le terminal. Pour sauvegarder les lexems dans un fichier, ajoutez l'argument `--save` :
  ```bash
  python3 Lexer/lexer.py examples/hello.carlos --save
  ```
  Les lexems seront sauvegardés dans le dossier `Lexer/examples_lexed`.

### 2. Analyse syntaxique (Parser)

L'analyse syntaxique prend les lexèmes produits par le lexer et construit un arbre syntaxique abstrait (AST). Cet AST représente la structure hiérarchique du programme.

- **Fichier principal** : `Parser/parser.py`
- **Exemple d'utilisation** :
  ```bash
  python3 Parser/parser.py examples/hello.carlos
  ```
  Cela affiche l'AST dans le terminal. Pour sauvegarder l'AST dans un fichier, ajoutez l'argument `--save` :
  ```bash
  python3 Parser/parser.py examples/hello.carlos --save
  ```
  L'AST sera sauvegardé dans le dossier `Parser/examples_parsed`.

---

### 3. Visiteurs (Visitors)

Les visiteurs parcourent l'AST pour effectuer diverses tâches, comme :

- **Pretty-printer** : Regénère le code source en Carlos à partir de l'AST.
  - **Fichier** : `Visitors/PrettyPrinter.py`
- **Générateur de code JavaScript** : Convertit le code Carlos en code JavaScript.
  - **Fichier** : `Visitors/JSCodeGenerator.py`

Exemple d'utilisation pour le pretty-printer :

```bash
python3 Visitors/PrettyPrinter.py examples/hello.carlos --save
```

---

### 4. Génération de code JavaScript

La phase finale consiste à utiliser le générateur de code JavaScript pour obtenir le code JavaScript final. Celui-ci pourra ensuite être exécuté grâce à Node.js. Exemple d'utilisation :

```bash
python3 Visitors/JSCodeGenerator.py examples/hello.carlos --save
```

Le code JavaScript sera sauvegardé dans le dossier `Visitors/examples_js`. Il peut ensuite être exécuté avec Node.js.

Exemple d'utilisation :

```bash
node Visitors/examples_js/hello.js
```

---

### 5. Compilation puis exécution

Pour compiler un fichier Carlos et l'exécuter, vous pouvez utiliser le fichier `compiler.py` :

```bash
python3 compiler.py examples/hello.carlos
```

Le code JavaScript sera ensuite exécuté avec Node.js.

Pour sauvegarder le code JavaScript, ajoutez l'argument `--save` :

```bash
python3 compiler.py examples/hello.carlos --save
```

Le code JavaScript sera sauvegardé dans le dossier `Visitors/examples_js`.

## Exemples

Des exemples de code source en Carlos sont disponibles dans le dossier `examples`. Ces examples proviennent des examples présents sur le projet Carlos décrit en sources. Un example additionnel nommé `complex.carlos` à été généré par ChatGPT pour implémenter un maximum des fonctionnalités possibles par le code Carlos.

Pour tester les différentes étapes de compilation sur les différents exemples, les différents fichiers nommés `lex_examples.py`, `parse_examples.py`, `create_JS_files_from_examples.py` et `PrettyPrint_examples.py` sont disponibles dans leurs dossiers respectifs. Ils effectuent leurs tâches respectives sur l'intégralité des fichiers présents dans le dossier `examples` et sauvegardent les résultats dans leurs dossiers examples respectifs.

Pour tester ces exemples, vous pouvez utiliser les commandes suivantes :

```bash
python3 Lexer/lex_examples.py
python3 Parser/parse_examples.py
python3 Visitors/create_JS_files_from_examples.py
python3 Visitors/PrettyPrint_examples.py
```

---

## Objectif du projet

L'objectif principal est de convertir le code Carlos en code JavaScript pour permettre son exécution.

---

## Sources

Les différentes sources utilisées pour la compréhension du langage Carlos ainsi que les liens vers d'autres projets utilisant le langage Carlos sont disponibles ici :

- https://cs.lmu.edu/~ray/notes/carlos/
- https://github.com/rtoal/carlos/
