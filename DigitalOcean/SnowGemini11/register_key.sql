-- Run in a Snowflake worksheet (Snowsight) while logged in via Google SSO.

-- 1. Find your exact login name (use this as SNOWFLAKE_USER in .env)
SELECT CURRENT_USER();
SET me = '"' || CURRENT_USER() || '"';

-- 2. Attach the public key to your user (needs ACCOUNTADMIN/SECURITYADMIN if not your own user)
ALTER USER IDENTIFIER($me) SET RSA_PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAttrQ6Z5dVx0j6L1+rvymFKJmTL02MGwgtRXQYW0dbh07weTirBLEfdocdsRuN577O5XxGrXBui6TZYTtdayxo+/AtegM2lFVGQ8XIO8fbv1n+LKg8C90d4XMmr4P/a9T5jtbQVLij4NL+tjfN5R4SWCes1JurCrNzcoR5+Gb+xUOjTVELuVnBmAw9EbBJrUcjOgLdb9HHk9UwzV58kjhQGMPTLU/qG8KRkYOlywuVAN9ENJD6sMAoF6p1HPFoCgYCmeOdIIYbHYHuS8ty+dxIGWi4NJtiwF4WaXk6qB+C+6yWdjZfM6JOu3DG6xKZ50tdGxoeCMW2X1PoWpdvaJRuQIDAQAB';

-- 3. Verify: RSA_PUBLIC_KEY_FP should equal SHA256:Xr9IpAzu8naUZFax3B0UiDErozXKfly5AjbloXbDeZU=
DESC USER IDENTIFIER($me);
