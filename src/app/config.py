import re
from datetime import timedelta


PUBCHEM_API_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
SYNONYMS_ENDPOINT_TEMPLATE = "compound/name/{compound_name}/synonyms/JSON"

# regex for CAS pattern (e.g., 'CAS-50-00-0')
CAS_PATTERN = re.compile(r"(CAS-)?(?P<number>\d{2,7}-\d{2}-\d)")

CACHE_EXPIRE_AFTER = timedelta(hours=1)
RATE_LIMIT_PER_SECOND = 4