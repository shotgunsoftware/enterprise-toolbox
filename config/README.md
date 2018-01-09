**Untar docker-shotgun* images**
**Load shotgun images**
**Modify docker-compose.yml**
  - Uncomment 
    - transcoder server
    - transcoder worker

  - Modify
    - SHOTGUN_SITE_URL
    - POSTGRESQL_HOST
    - OVPNFILENAME 

#Tested
  - Docker Release 7.6.0.0
  - Docker Release 7.5.2.0
  - Docker Release 7.4.3.0
