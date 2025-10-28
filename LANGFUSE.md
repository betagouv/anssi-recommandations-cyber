# 📊 Configuration Langfuse

Langfuse est intégré au projet pour le monitoring et l'observabilité des interactions avec l'IA.

## 🚀 Démarrage rapide

1. **Configurer les variables d'environnement** :
   ```bash
   cp .env.langfuse .env.langfuse.local
   # Modifier les mots de passe dans .env.langfuse.local
   ```

2. **Lancer Langfuse** :
   ```bash
   docker network create anssi-net
   docker compose --env-file .env.langfuse -f docker-compose-langfuse.yml up -d
   ```

3. **Accéder à l'interface** :
   - Interface Langfuse : http://localhost:3002
   - Console MinIO : http://localhost:9093

## 🔧 Configuration

### Ports utilisés
- **Langfuse Web** : 3002 (au lieu de 3000 pour éviter les conflits)
- **Langfuse Worker** : 3031
- **PostgreSQL** : 5434 (au lieu de 5432)
- **ClickHouse** : 8124 et 9001
- **MinIO** : 9092 et 9093
- **Redis** : 6380

### Variables importantes à modifier
Dans `.env.langfuse`, changez obligatoirement :
- `SALT` : Générer avec `openssl rand -hex 16`
- `ENCRYPTION_KEY` : Générer avec `openssl rand -hex 32`
- `NEXTAUTH_SECRET` : Générer avec `openssl rand -hex 32`
- Tous les mots de passe (`*_PASSWORD`, `*_SECRET`)

## 🛠️ Commandes utiles

```bash
# Démarrer Langfuse
docker compose -f docker-compose-langfuse.yml up -d

# Arrêter Langfuse
docker compose -f docker-compose-langfuse.yml down

# Voir les logs
docker compose -f docker-compose-langfuse.yml logs -f

# Redémarrer un service spécifique
docker compose -f docker-compose-langfuse.yml restart langfuse-web
```

## 🔗 Intégration avec le projet

Le monitoring Langfuse est déjà intégré au service Albert !

### Configuration
1. **Obtenez vos clés API** :
   ```bash
   ./obtenir-cles-langfuse.sh
   ```

2. **Ajoutez les variables à votre .env** :
   ```bash
   LANGFUSE_PUBLIC_KEY=pk-lf-votre_cle_publique
   LANGFUSE_SECRET_KEY=sk-lf-votre_cle_secrete
   LANGFUSE_HOST=http://localhost:3002
   ```

3. **Redémarrez votre application** :
   ```bash
   docker compose restart mqc-backend
   ```

### Fonctionnalités tracées
- ✅ **Recherche de paragraphes** : Question, nombre de résultats, scores de similarité
- ✅ **Génération de réponses** : Question, réponse, sources utilisées, durée
- ✅ **Métadonnées** : Documents sources, pages, durées d'exécution

## 🔒 Sécurité

- Tous les services sont configurés pour n'être accessibles que depuis localhost
- Changez tous les mots de passe par défaut
- En production, utilisez des secrets externes (AWS Secrets Manager, etc.)
- Les clés API Langfuse doivent être gardées secrètes