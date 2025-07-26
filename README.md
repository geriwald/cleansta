# Mode d'emploi pour utiliser le script Cleansta sur Mac

Ce guide explique étape par étape comment utiliser le script `main.py` pour nettoyer les messages Instagram, même si tu n'es pas développeur. Suis simplement chaque étape dans l'ordre.

---

## 0. Télécharger le script depuis GitHub

1. Va sur la page du projet : [https://github.com/geriwald/cleansta](https://github.com/geriwald/cleansta)
2. Clique sur le bouton vert **Code** puis sur **Download ZIP** pour télécharger tout le projet.
3. Décompresse le fichier ZIP sur ton Bureau (ou ailleurs), tu obtiendras un dossier `cleansta` contenant le script `main.py`.

Ou bien, pour télécharger uniquement le script principal :

[Télécharger main.py directement](https://github.com/geriwald/cleansta/raw/main/main.py)

Place le fichier téléchargé dans un dossier dédié, par exemple sur ton Bureau.

---

## 1. Vérifier l'installation de Python

1. Ouvre le Terminal (Applications > Utilitaires > Terminal).
2. Tape :

   ```bash
   python3 --version
   ```

   - Si tu vois une version (ex : `Python 3.9.6`), c'est bon !
   - Sinon, va sur [https://www.python.org/downloads/](https://www.python.org/downloads/) et installe Python.

---

## 2. Préparer le dossier de travail

1. Crée un dossier sur ton Bureau, par exemple appelé `cleansta`.
2. Place le fichier `main.py` (ou le contenu du ZIP) dans ce dossier.

---

## 3. Créer un environnement virtuel (venv)

1. Dans le Terminal, va dans le dossier du projet :

   ```bash
   cd ~/Desktop/cleansta
   ```

2. Crée un environnement virtuel :

   ```bash
   python3 -m venv venv
   ```

3. Active l'environnement virtuel :

   ```bash
   source venv/bin/activate
   ```

   - Tu devrais voir le préfixe `(venv)` devant la ligne de commande.

---

## 4. Installer les dépendances

1. Installe Playwright dans l'environnement virtuel :

   ```bash
   pip install playwright
   ```

2. Installe les navigateurs nécessaires pour Playwright :

   ```bash
   python -m playwright install
   ```

---

## 5. Lancer le script

1. Toujours dans le Terminal, dans le dossier du projet et avec le venv activé :

   ```bash
   python main.py
   ```

2. Suis les instructions affichées (connecte-toi à Instagram dans la fenêtre qui s'ouvre, puis appuie sur Entrée).

---

## 6. Conseils

- Si tu as un problème, copie le message d'erreur et demande de l'aide.
- Tu peux relancer le script autant de fois que nécessaire.
- Les logs sont enregistrés dans des fichiers `.log` dans le dossier du projet.

---

Voilà, tu es prêt à utiliser le script dans un environnement propre et isolé !
