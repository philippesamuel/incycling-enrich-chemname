from datetime import timedelta

PUBCHEM_API_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
SYNONYMS_ENDPOINT_TEMPLATE = "compound/name/{compound_name}/synonyms/JSON"

CACHE_EXPIRE_AFTER = timedelta(hours=1)
RATE_LIMIT_PER_SECOND = 4
