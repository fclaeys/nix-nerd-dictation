# nerd-dictation Nix Flake

> **⚠️ WORK IN PROGRESS / TRAVAIL EN COURS**
>
> **🇬🇧 This project is currently a work in progress and only functions under specific conditions:**
> - ✅ Tested on Linux with Wayland (COSMIC DE)
> - ✅ Works with PulseAudio/PipeWire audio systems
> - ⚠️ May require audio system configuration
> - ⚠️ Microphone permissions needed
> - 🇫🇷 Currently optimized for French language only
>
> **🇫🇷 Ce projet est actuellement en cours de développement et ne fonctionne que dans certaines conditions :**
> - ✅ Testé sur Linux avec Wayland (COSMIC DE)
> - ✅ Fonctionne avec les systèmes audio PulseAudio/PipeWire
> - ⚠️ Peut nécessiter une configuration du système audio
> - ⚠️ Permissions microphone requises
> - 🇫🇷 Actuellement optimisé pour le français uniquement

Ce flake Nix fournit un package et des modules NixOS/Home Manager pour [nerd-dictation](https://github.com/ideasman42/nerd-dictation), un outil de dictée vocale hors ligne.

## ✅ Installation complètement automatisée

VOSK et le modèle français sont maintenant inclus automatiquement dans le package !

- ✅ VOSK 0.3.45 inclus
- ✅ Modèle français `vosk-model-small-fr-0.22` inclus
- 🎯 **Détection automatique Wayland/X11** pour l'injection de texte
- 🇫🇷 **Configuration française automatique** avec ponctuation et conversion des nombres
- 🚀 Prêt à l'emploi sans configuration

## Utilisation

### Package seul

```bash
nix run github:fclaeys/nix-nerd-dictation
```

### Module NixOS

```nix
{
  inputs.nerd-dictation.url = "github:fclaeys/nix-nerd-dictation";

  imports = [ inputs.nerd-dictation.nixosModules.default ];

  services.nerd-dictation = {
    enable = true;
    audioBackend = "parec";  # ou "sox", "pw-cat"
    inputBackend = "xdotool"; # ou "ydotool", "dotool", "wtype"
  };
}
```

### Module Home Manager

```nix
{
  imports = [ inputs.nerd-dictation.homeManagerModules.default ];

  programs.nerd-dictation = {
    enable = true;
    inputBackend = "wtype";   # Wayland
    audioBackend = "parec";   # PulseAudio/PipeWire
  };
}
```

## Configuration

### Options principales

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `audioBackend` | enum | `"parec"` | Backend audio (`parec`, `sox`, `pw-cat`) |
| `inputBackend` | enum | `"xdotool"` | Backend d'entrée (`xdotool`, `ydotool`, `dotool`, `wtype`) |
| `configScript` | lines | *(config française)* | Script Python de configuration (voir ci-dessous) |
| `modelPath` | string/null | `null` | Chemin vers un modèle VOSK personnalisé |
| `timeout` | int | `1000` | Timeout en ms pour la reconnaissance vocale |
| `idleTime` | int | `500` | Temps d'inactivité avant arrêt de l'enregistrement |

### Détection automatique de l'environnement

Le package détecte automatiquement votre environnement graphique :
- **Wayland** (COSMIC, GNOME, Sway, etc.) → utilise `wtype`
- **X11** (i3, XFCE, etc.) → utilise `xdotool`

### Configuration française automatique

La configuration française est déployée automatiquement par le module et mise à jour à chaque rebuild. Elle inclut :

#### Ponctuation

| Vous dites | Résultat |
|------------|----------|
| "virgule" | `,` |
| "point" | `.` |
| "point d'interrogation" | ` ?` |
| "point d'exclamation" | ` !` |
| "deux points" | ` :` |
| "point virgule" | ` ;` |
| "tiret" | `-` |

#### Symboles

| Vous dites | Résultat |
|------------|----------|
| "arobase" | `@` |
| "diese" | `#` |
| "pourcentage" | `%` |
| "et commercial" | `&` |
| "plus" / "égal" / "moins" | `+` / `=` / `-` |

#### Navigation

| Vous dites | Résultat |
|------------|----------|
| "nouvelle ligne" / "retour à la ligne" | retour à la ligne |
| "tabulation" | tabulation |
| "parenthèse ouverte" / "fermée" | `(` / `)` |
| "guillemet ouvrant" / "fermant" | `"` |

#### Conversion des nombres français

Le parseur convertit automatiquement les nombres dictés en français vers des chiffres. Il gère l'ensemble du système numérique français, y compris les formes composées :

| Vous dites | Résultat |
|------------|----------|
| "quarante-deux mille six cent quatre-vingt-sept" | `42687` |
| "quatre-vingt-quinze" | `95` |
| "deux cent vingt-trois" | `223` |
| "mille" | `1000` |
| "un million deux cent mille trois" | `1200003` |
| "vingt et un" | `21` |
| "soixante et onze" | `71` |
| "quatre-vingt-dix-neuf" | `99` |

Les nombres sont correctement composés quel que soit leur position dans la phrase : "il y a vingt-trois personnes" → "il y a 23 personnes".

#### Exemples de dictée complète

- "Bonjour virgule comment allez-vous point d'interrogation" → "Bonjour, comment allez-vous ?"
- "J'ai quarante-deux ans point" → "J'ai 42 ans."
- "Article trois deux points nouvelle ligne" → "Article 3 :\n"

### Configuration personnalisée

Pour remplacer la configuration par défaut, définissez `configScript` :

```nix
programs.nerd-dictation = {
  enable = true;
  configScript = ''
    def nerd_dictation_process(text):
        text = text.replace(" new line", "\n")
        text = text.replace(" comma", ",")
        return text
  '';
};
```

### Raccourcis clavier (Home Manager)

Le module Home Manager peut configurer automatiquement les raccourcis clavier pour i3 et sway :

```nix
programs.nerd-dictation.keyBindings = {
  "ctrl+alt+d" = "nerd-dictation begin";
  "ctrl+alt+shift+d" = "nerd-dictation end";
};
```

### Service systemd

Le module NixOS crée un service système, tandis que le module Home Manager peut créer un service utilisateur optionnel.

## Alias shell

Le module Home Manager ajoute automatiquement des alias pratiques :
- `nd-begin` : Démarrer la dictée
- `nd-end` : Arrêter la dictée
- `nd-suspend` : Suspendre/reprendre la dictée
