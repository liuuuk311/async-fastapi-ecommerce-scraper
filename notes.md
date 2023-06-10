pg_dump -U postgres -d postgres -t search_brand -t search_clickedproduct -t search_continent -t search_country -t search_importquery -t search_requestedstore -t search_shippingmethod -t search_shippingzone -t search_shippingzone_ship_to -t search_store -a -Fc -f fpvfinder_dump_29052023.sql

docker cp 697e22fdb382:/fpvfinder_dump_29052023.sql ./fpvfinder_dump_29052023.sql

scp -r do_fpvfinder:/home/deployer/fpvfinder_dump_29052023.sql ~/Projects/personal/FPVfinderV2/backend

docker cp ../fpvfinder_dump_29052023.sql c6a10232ff8e:/dump.sql

psql -U postgres -d postgres -f dump.sql
