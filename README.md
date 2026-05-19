# RGPD – Base documentaire CNRS / EPST

> **Objectif** : Recenser les sources officielles (réglementation européenne et française, CNIL, CEPD, CNRS) applicables au traitement de données à caractère personnel dans un EPST, avec un focus sur les données génétiques produites en recherche (ex. RNA-Seq) sans finalité d'étude génétique.

## ⚠️ Important – Données génétiques et anonymisation

Le RGPD qualifie expressément les **données génétiques** de « catégories particulières de données » (données sensibles, art. 9). Une conséquence majeure est que, dès lors qu'un traitement produit ou manipule des données génétiques, la notion d'**anonymisation** au sens du RGPD devient quasiment impossible à atteindre de manière irréversible (ré-identification par croisement génomique). La **pseudonymisation** est alors la mesure de sécurité attendue, sans que cela fasse tomber le jeu de données hors du champ du RGPD.

## 📁 Organisation des fichiers BibTeX

- **`legislations.bib`** – Textes législatifs et réglementaires (UE & FR)
- **`cnil.bib`** – Méthodologies de référence, délibérations et recommandations CNIL
- **`cepd.bib`** – Lignes directrices du Comité européen de la protection des données (CEPD / EDPB)
- **`cnrs.bib`** – Chartes et référentiels du CNRS / EPST

## 🔍 Cas d'usage cible

- Études d'expression (RNA-Seq) à partir de matériel biologique initialement anonymisé mais générant des données génétiques
- Recherche en infectiologie / bio-informatique dans un laboratoire CNRS
- Conformité EPST : finalité de recherche scientifique, base légale, minimisation, sécurité

## 🛠️ Utilisation

```bash
# Compiler une bibliographie LaTeX
pdflatex main.tex
bibtex legislations
bibtex cnil
bibtex cepd
bibtex cnrs
pdflatex main.tex
```

## 📥 Script de téléchargement

Le script `fetch_resources.py` parse les fichiers `.bib` et télécharge automatiquement les ressources (PDF/HTML) dans `downloads/<catégorie>/`.

```bash
python fetch_resources.py
```

Options :
- `--no-verify-ssl` : désactive la vérification SSL (utile pour certains sites CNRS avec certificats internes)

### Limitations connues
- **Légifrance** et **EUR-Lex** bloquent les requêtes automatisées (403 / challenge anti-bot). Les textes législatifs doivent être téléchargés manuellement ou via un navigateur.
- Le script injecte un champ `file = {downloads/...}` dans chaque entrée BibTeX pour pointer vers la copie locale quand le téléchargement réussit.

## 📜 Licence

Les données bibliographiques sont des métadonnées de documents publics. Ce recueil est fourni en licence **CC0 1.0 Universal**.
